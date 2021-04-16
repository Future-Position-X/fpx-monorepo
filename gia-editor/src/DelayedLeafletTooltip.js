/* eslint-disable */
L.Layer.include({

    showDelay: 1200,
    hideDelay: 100,

    bindTooltipDelayed: function (content, options) {
        if (content instanceof L.Tooltip) {
            L.setOptions(content, options);
            this._tooltip = content;
            content._source = this;
        } else {
            if (!this._tooltip || options) {
                this._tooltip = new L.Tooltip(options, this);
            }
            this._tooltip.setContent(content);

        }

        this._initTooltipInteractionsDelayed();

        if (this._tooltip.options.permanent && this._map && this._map.hasLayer(this)) {
            this.openTooltipWithDelay();
        }

        return this;
    },

    _openTooltipDelayed: function (e) {
        var layer = e.layer || e.target;

        if (!this._tooltip || !this._map) {
            return;
        }
        this.openTooltipWithDelay(layer, this._tooltip.options.sticky ? e.latlng : undefined);
    },

    openTooltipDelayed: function (layer, latlng) {
        if (!(layer instanceof L.Layer)) {
            latlng = layer;
            layer = this;
        }
        if (layer instanceof L.FeatureGroup) {
            for (var id in this._layers) {
                layer = this._layers[id];
                break;
            }
        }
        if (!latlng) {
            latlng = layer.getCenter ? layer.getCenter() : layer.getLatLng();
        }
        if (this._tooltip && this._map) {
            this._tooltip._source = layer;
            this._tooltip.update();
            this._map.openTooltip(this._tooltip, latlng);
            if (this._tooltip.options.interactive && this._tooltip._container) {
                addClass(this._tooltip._container, 'leaflet-clickable');
                this.addInteractiveTarget(this._tooltip._container);
            }
        }

        return this;
    },
    openTooltipWithDelay: function (t, i) {
        this._delay(this.openTooltipDelayed, this, this.showDelay, t, i);
    },
    closeTooltipDelayed: function () {
        if (this._tooltip) {
            this._tooltip._close();
            if (this._tooltip.options.interactive && this._tooltip._container) {
                removeClass(this._tooltip._container, 'leaflet-clickable');
                this.removeInteractiveTarget(this._tooltip._container);
            }
        }
        return this;
    },
    closeTooltipWithDelay: function () {
        clearTimeout(this._timeout);
        this._delay(this.closeTooltipDelayed, this, this.hideDelay);
    },
    _delay: function (func, scope, delay, t, i) {
        var me = this;
        if (this._timeout) {
            clearTimeout(this._timeout)
        }
        this._timeout = setTimeout(function () {
            func.call(scope, t, i);
            delete me._timeout
        }, delay)
    },
    _initTooltipInteractionsDelayed: function (remove$$1) {
        if (!remove$$1 && this._tooltipHandlersAdded) { return; }
        var onOff = remove$$1 ? 'off' : 'on',
           events = {
               remove: this.closeTooltipWithDelay,
               move: this._moveTooltip
           };
        if (!this._tooltip.options.permanent) {
            events.mouseover = this._openTooltipDelayed;
            events.mouseout = this.closeTooltipWithDelay;
            events.click = this.closeTooltipWithDelay;
            if (this._tooltip.options.sticky) {
                events.mousemove = this._moveTooltip;
            }
            if (L.touch) {
                events.click = this._openTooltipDelayed;
            }
        } else {
            events.add = this._openTooltipDelayed;
        }
        this[onOff](events);
        this._tooltipHandlersAdded = !remove$$1;
    }
});