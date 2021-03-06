/* eslint no-underscore-dangle: ["error", { "enforceInMethodNames": false, "allowAfterThis": true}] */
/* eslint-disable no-param-reassign */

// Leaflet-SVGIcon
// SVG icon for any marker class
// Ilya Atkin
// ilya.atkin@unh.edu
// https://github.com/iatkin/leaflet-svgicon

import * as L from 'leaflet';

L.DivIcon.SVGIcon = L.DivIcon.extend({
  options: {
    circleText: '',
    className: 'svg-icon',
    circleAnchor: null, // defaults to [iconSize.x/2, iconSize.x/2]
    circleColor: null, // defaults to color
    circleOpacity: null, // defaults to opacity
    circleFillColor: 'rgb(255,255,255)',
    circleFillOpacity: null, // default to opacity
    circleRatio: 0.5,
    circleWeight: null, // defaults to weight
    color: 'rgb(0,102,255)',
    fillColor: null, // defaults to color
    fillOpacity: 0.4,
    fontColor: 'rgb(0, 0, 0)',
    fontOpacity: '1',
    fontSize: null, // defaults to iconSize.x/4
    fontWeight: 'normal',
    iconAnchor: null, // defaults to [iconSize.x/2, iconSize.y] (point tip)
    iconSize: L.point(32, 48),
    opacity: 1,
    popupAnchor: null,
    weight: 2,
  },
  initialize(options) {
    options = L.Util.setOptions(this, options);

    // iconSize needs to be converted to a Point object if it is not passed as one
    options.iconSize = L.point(options.iconSize);

    // in addition to setting option dependant defaults, Point-based options are converted to Point objects
    if (!options.circleAnchor) {
      options.circleAnchor = L.point(
        Number(options.iconSize.x) / 2,
        Number(options.iconSize.x) / 2
      );
    } else {
      options.circleAnchor = L.point(options.circleAnchor);
    }
    if (!options.circleColor) {
      options.circleColor = options.color;
    }
    if (!options.circleFillOpacity) {
      options.circleFillOpacity = options.opacity;
    }
    if (!options.circleOpacity) {
      options.circleOpacity = options.opacity;
    }
    if (!options.circleWeight) {
      options.circleWeight = options.weight;
    }
    if (!options.fillColor) {
      options.fillColor = options.color;
    }
    if (!options.fontSize) {
      options.fontSize = Number(options.iconSize.x / 4);
    }
    if (!options.iconAnchor) {
      options.iconAnchor = L.point(Number(options.iconSize.x) / 2, Number(options.iconSize.y));
    } else {
      options.iconAnchor = L.point(options.iconAnchor);
    }
    if (!options.popupAnchor) {
      options.popupAnchor = L.point(0, -0.75 * options.iconSize.y);
    } else {
      options.popupAnchor = L.point(options.popupAnchor);
    }

    options.html = this._createSVG();
  },
  _createCircle() {
    const cx = Number(this.options.circleAnchor.x);
    const cy = Number(this.options.circleAnchor.y);
    const radius = (this.options.iconSize.x / 2) * Number(this.options.circleRatio);
    const fill = this.options.circleFillColor;
    const fillOpacity = this.options.circleFillOpacity;
    const stroke = this.options.circleColor;
    const strokeOpacity = this.options.circleOpacity;
    const strokeWidth = this.options.circleWeight;
    const className = `${this.options.className}-circle`;

    const circle = `<circle class="${className}" cx="${cx}" cy="${cy}" r="${radius}" fill="${fill}" fill-opacity="${fillOpacity}" stroke="${stroke}" stroke-opacity=${strokeOpacity}" stroke-width="${strokeWidth}"/>`;

    return circle;
  },
  _createPathDescription() {
    const height = Number(this.options.iconSize.y);
    const width = Number(this.options.iconSize.x);
    const weight = Number(this.options.weight);
    const margin = weight / 2;

    const startPoint = `M ${margin} ${width / 2} `;
    const leftLine = `L ${width / 2} ${height - weight} `;
    const rightLine = `L ${width - margin} ${width / 2} `;
    const arc = `A ${width / 4} ${width / 4} 0 0 0 ${margin} ${width / 2} Z`;

    const d = startPoint + leftLine + rightLine + arc;

    return d;
  },
  _createPath() {
    const pathDescription = this._createPathDescription();
    const strokeWidth = this.options.weight;
    const stroke = this.options.color;
    const strokeOpacity = this.options.opacity;
    const fill = this.options.fillColor;
    const { fillOpacity } = this.options;
    const className = `${this.options.className}-path`;

    const path = `<path class="${className}" d="${pathDescription}" stroke-width="${strokeWidth}" stroke="${stroke}" stroke-opacity="${strokeOpacity}" fill="${fill}" fill-opacity="${fillOpacity}"/>`;

    return path;
  },
  _createSVG() {
    const path = this._createPath();
    const circle = this._createCircle();
    const text = this._createText();
    const className = `${this.options.className}-svg`;

    const style = `width:${this.options.iconSize.x}px; height:${this.options.iconSize.y}px;`;

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" version="1.1" class="${className}" style="${style}">${path}${circle}${text}</svg>`;

    return svg;
  },
  _createText() {
    const fontSize = `${this.options.fontSize}px`;
    const { fontWeight } = this.options;
    const lineHeight = Number(this.options.fontSize);

    const { x } = this.options.circleAnchor;
    const y = this.options.circleAnchor.y + lineHeight * 0.35; // 35% was found experimentally
    const { circleText } = this.options;
    const textColor = this.options.fontColor
      .replace('rgb(', 'rgba(')
      .replace(')', `,${this.options.fontOpacity})`);

    const text = `<text text-anchor="middle" x="${x}" y="${y}" style="font-size: ${fontSize}; font-weight: ${fontWeight}" fill="${textColor}">${circleText}</text>`;

    return text;
  },
});

L.divIcon.svgIcon = (options) => new L.DivIcon.SVGIcon(options);

L.Marker.SVGMarker = L.Marker.extend({
  options: {
    iconFactory: L.divIcon.svgIcon,
    iconOptions: {},
  },
  initialize(latlng, options) {
    options = L.Util.setOptions(this, options);
    options.icon = options.iconFactory(options.iconOptions);
    this._latlng = latlng;
  },
  onAdd(map) {
    L.Marker.prototype.onAdd.call(this, map);
  },
  setStyle(style) {
    if (this._icon) {
      // var svg = this._icon.children[0]
      const iconBody = this._icon.children[0].children[0];
      const iconCircle = this._icon.children[0].children[1];

      if (style.color && !style.iconOptions) {
        const stroke = style.color
          .replace('rgb', 'rgba')
          .replace(')', `,${this.options.icon.options.opacity})`);
        const fill = style.color
          .replace('rgb', 'rgba')
          .replace(')', `,${this.options.icon.options.fillOpacity})`);
        iconBody.setAttribute('stroke', stroke);
        iconBody.setAttribute('fill', fill);
        iconCircle.setAttribute('stroke', stroke);

        this.options.icon.fillColor = fill;
        this.options.icon.color = stroke;
        this.options.icon.circleColor = stroke;
      }
      if (style.opacity) {
        this.setOpacity(style.opacity);
      }
      if (style.iconOptions) {
        if (style.color) {
          style.iconOptions.color = style.color;
        }
        const iconOptions = L.Util.setOptions(this.options.icon, style.iconOptions);
        this.setIcon(L.divIcon.svgIcon(iconOptions));
      }
    }
  },
});

L.marker.svgMarker = (latlng, options) => new L.Marker.SVGMarker(latlng, options);

const { svgMarker } = L.marker;

export { svgMarker as default };
