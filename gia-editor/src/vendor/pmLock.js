/* eslint-disable */
L.PMLock = L.Class.extend({
    options: {
        position: undefined,
        text: {
            unlock: "Unlock",
            lock: "Lock",
            title: "Lock / Unlock Layers",
            finish: "Finish"
        },
        showControl: true,
    },
    activeMode: '',
    toolbarBtn: undefined,
    cssadded: false,
    initialize(map, options) {
        this.map = map;
        if(options && options.text) {
            options.text = this.setText(options.text);
        }
        L.setOptions(this, options);
        this.overwriteFunctions();

        this.render();
    },
    setOptions: function(options){
        if(options && options.text) {
            options.text = this.setText(options.text);
        }
        L.setOptions(this, options);
        this.render();
    },
    render: function(){
        this.activeMode = '';
        if(this.toolbarBtn) {
            this.toolbarBtn.onRemove();
            this.toolbarBtn = undefined;
        }
        if(this.options.showControl) {
            this.addCss();
            this.createControl();
        }
    },
    setText: function(text){
        if(text.unlock){
            this.options.text.unlock = text.unlock;
        }
        if(text.lock){
            this.options.text.lock = text.lock;
        }
        if(text.title){
            this.options.text.title = text.title;
        }
        if(text.finish){
            this.options.text.finish = text.finish;
        }
        this.render();
        return this.options.text;
    },
    enableLock: function(name,changeToolbar = true){
        if(!name){
            name = 'lock';
        }
        var that = this;
        var layers = this.findLayers(this.map,true);
        this.markBtnAction(name);
        layers.forEach(function (layer) {
           layer.on('click',that.clickFnc,that)
        });
        if(changeToolbar && this.toolbarBtn){
            this.toolbarBtn.toggle(true);
        }
    },
    disableLock: function(changeToolbar = true){
        var that = this;
        var layers = this.findLayers(this.map,true);
        this.markBtnAction();
        layers.forEach(function (layer) {
            layer.off('click',that.clickFnc,that)
        });

        if(changeToolbar && this.toolbarBtn){
            this.toolbarBtn.toggle(false);
        }
    },
    toggle: function(name = 'lock', changeToolbar=true){
        if(this.activeMode === ""){
            this.enableLock(name,changeToolbar);
        }else{
            this.disableLock(changeToolbar);
        }
    },
    clickFnc: function(e){
        if(this.activeMode === "lock") {
            e.target.options.pmLock = true;
        }else if(this.activeMode === "unlock"){
            e.target.options.pmLock = false;
        }
    },
    markBtnAction: function(name){
        //Clear active btn
        var allBtns = document.getElementsByClassName('leaflet-pm-action');
        if(allBtns.length > 0) {
            for(var i = 0; i < allBtns.length; i++){
                L.DomUtil.removeClass(allBtns[i],'pmLock-active');
            }
        }

        if(name) {
            this.activeMode = name;
            var elms = document.getElementsByClassName('action-' + name);
            if (elms.length > 0) {
                var elm = elms[0];
                L.DomUtil.addClass(elm, 'pmLock-active');
            }
        }else{
            this.activeMode = "";
        }
    },
    findLayers: function(map, ignoreLock = false) {
        let layers = [];
        map.eachLayer(layer => {
            if (
                layer instanceof L.Polyline ||
                layer instanceof L.Marker ||
                layer instanceof L.Circle ||
                layer instanceof L.CircleMarker
            ) {
                layers.push(layer);
            }
        });

        // filter out layers that don't have the leaflet-geoman instance
        layers = layers.filter(layer => !!layer.pm);

        // filter out everything that's leaflet-geoman specific temporary stuff
        layers = layers.filter(layer => !layer._pmTempLayer);

        /**
         * pmLock
         * filter out every layer that's locked
         */
        if (!ignoreLock) {
            layers = layers.filter(layer => layer.options.pmLock !== true);
        }

        return layers;
    },
    getLockedLayers: function(){
      var layers = this.findLayers(this.map,true);
      return layers.filter(layer => layer.options.pmLock === true);
    },
    getUnlockedLayers: function(){
        return this.findLayers(this.map);
    },
    createControl: function(){
        this.map.options.position = this.map.pm.Toolbar.options.position;
        this.map.pm.Toolbar.options['pmLockButton'] = true;
        this.lockContainer = L.DomUtil.create(
            'div',
            'leaflet-pm-toolbar leaflet-pm-options leaflet-bar leaflet-control'
        );

        const lockButton = {
            className: 'control-icon leaflet-pm-icon-pmLock',
            title: this.options.text.title,
            onClick: () => {
            },
            afterClick: () => {
                this.toggle();
            },
            tool: 'edit',
            doToggle: true,
            toggleStatus: false,
            disableOtherButtons: true,
            position: this.options.position,
            actions: [],
        };
        this.toolbarBtn = new L.Control.PMButton(lockButton);
        this.map.pm.Toolbar._addButton('pmLockButton', this.toolbarBtn);
        this.map.pm.Toolbar._showHideButtons = this._extend(this.map.pm.Toolbar._showHideButtons,this._createActionBtn(this),this.map.pm.Toolbar);
        this.map.pm.Toolbar._showHideButtons();


    },
    _createActionBtn: function(that){
        return function() {
            const actions = [
                {
                    name: 'lock',
                    text: that.options.text.lock,
                    onClick() {
                        that.enableLock('lock');
                    },
                },
                {
                    name: 'unlock',
                    text: that.options.text.unlock,
                    onClick() {
                        that.enableLock('unlock');
                    },
                },
                {
                    name: 'finish',
                    text: that.options.text.finish,
                    onClick() {
                        that.toolbarBtn._triggerClick();
                    },
                },
            ];


            var actionContainer = that.toolbarBtn.buttonsDomNode.children[1];
            actionContainer.innerHTML = "";
            actions.forEach(action => {
                var name = action.name;
                const actionNode = L.DomUtil.create(
                    'a',
                    `leaflet-pm-action action-${name}`,
                    actionContainer
                );

                if (action.text) {
                    actionNode.innerHTML = action.text;
                } else {
                    actionNode.innerHTML = "Text not translated!";
                }


                L.DomEvent.addListener(actionNode, 'click', action.onClick, that);
                L.DomEvent.disableClickPropagation(actionNode);
            });
        }
    },
    _extend: function(fn,code,that){
        return function(){
            fn.apply(that,arguments);
            code.apply(that,arguments);
        }
    },
    overwriteFunctions: function () {
        var map = this.map;
        var that = this;

        map.pm.enableGlobalEditMode = function enableGlobalEditMode(o) {
            const options = {
                snappable: this._globalSnappingEnabled,
                ...o
            }

            const status = true;

            // Set toolbar button to currect status
            this.Toolbar.toggleButton('editMode', status);

            // find all layers handled by leaflet-geoman
            const layers = that.findLayers(this.map);

            // enable all layers
            layers.forEach(layer => {
                layer.pm.enable(options);
            });

            if (!this.throttledReInitEdit) {
                this.throttledReInitEdit = L.Util.throttle(this.handleLayerAdditionInGlobalEditMode, 100, this)
            }

            // handle layers that are added while in removal mode
            this.map.on('layeradd', this.throttledReInitEdit, this);

            this.setGlobalEditStatus(status);
        };
        map.pm.enableGlobalDragMode = function enableGlobalDragMode() {
            const layers = that.findLayers(this.map);

            this._globalDragMode = true;

            layers.forEach(layer => {
                layer.pm.enableLayerDrag();
            });

            if (!this.throttledReInitDrag) {
                this.throttledReInitDrag = L.Util.throttle(this.reinitGlobalDragMode, 100, this)
            }

            // add map handler
            this.map.on('layeradd', this.throttledReInitDrag, this);

            // toogle the button in the toolbar if this is called programatically
            this.Toolbar.toggleButton('dragMode', this._globalDragMode);

            this._fireDragModeEvent(true);
        };

        map.pm.enableGlobalRemovalMode = function enableGlobalRemovalMode() {
            const isRelevant = layer =>
                layer.pm &&
                !(layer.pm.options && layer.pm.options.preventMarkerRemoval) &&
                !(layer instanceof L.LayerGroup) &&
                layer.options.pmLock !== true;

            this._globalRemovalMode = true;
            // handle existing layers
            this.map.eachLayer(layer => {
                if (isRelevant(layer)) {
                    layer.on('click', this.removeLayer, this);
                }
            });

            if (!this.throttledReInitRemoval) {
                this.throttledReInitRemoval = L.Util.throttle(this.reinitGlobalRemovalMode, 100, this)
            }

            // handle layers that are added while in removal  xmode
            this.map.on('layeradd', this.throttledReInitRemoval, this);

            // toogle the button in the toolbar if this is called programatically
            this.Toolbar.toggleButton('deleteLayer', this._globalRemovalMode);

            this._fireRemovalModeEvent(true);
        }
    },
    addCss: function () {
        if(this.cssadded){
            return;
        }
        this.cssadded = true;

        var lockimg = "data:image/svg+xml;base64,PHN2ZwogICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDQ0OCA1MTIiPgogICAgPHBhdGggZmlsbD0iIzVCNUI1QiIKICAgICAgICAgIGQ9Ik00MDAgMjI0aC0yNHYtNzJDMzc2IDY4LjIgMzA3LjggMCAyMjQgMFM3MiA2OC4yIDcyIDE1MnY3Mkg0OGMtMjYuNSAwLTQ4IDIxLjUtNDggNDh2MTkyYzAgMjYuNSAyMS41IDQ4IDQ4IDQ4aDM1MmMyNi41IDAgNDgtMjEuNSA0OC00OFYyNzJjMC0yNi41LTIxLjUtNDgtNDgtNDh6bS0xMDQgMEgxNTJ2LTcyYzAtMzkuNyAzMi4zLTcyIDcyLTcyczcyIDMyLjMgNzIgNzJ2NzJ6IgogICAgICAgICAgY2xhc3M9IiI+PC9wYXRoPgo8L3N2Zz4=";
        var styles = ".leaflet-pm-toolbar .leaflet-pm-icon-pmLock {background-image: url('"+lockimg+"');margin: 5%;width: 90%;height: 90%;} .leaflet-pm-action.pmLock-active{background-color: #3d3d3d !important;}";

        var styleSheet = document.createElement("style");
        styleSheet.type = "text/css";
        styleSheet.innerText = styles;
        document.head.appendChild(styleSheet);
    }

});