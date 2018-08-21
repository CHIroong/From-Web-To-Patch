/**!
 * @file Support for finding element using absolute X/Y coordinates
 * @version 0.0.4
 * @copyright 2015 Kyle Welsby
 * @license MIT
 * @author Kyle Welsby <kyle@mekyle.com>
 */
(function() {
    'use strict';
  
    function closestFixed(elm) {
      if (window.getComputedStyle(elm).position === 'fixed') {
        return elm;
      } else {
        if (elm.parentElement && !/body|html/.test(elm.parentElement.tagName.toLowerCase())) {
          return closestFixed(elm.parentElement);
        } else {
          return null;
        }
      }
    }
    /**
     * @namespace document
     */
  
    /**
     * @function
     * @memberof document
     * @name elementFromAbsolutePoint
     * @description
     * Returns the element from the document whose elementFromPoint method
     * being called which is the topmost element which lies under the given
     * point.
     * To get an element, specify the point via coordinates, in CSS pixels,
     * relative to the upper-left-most point in the window or frame containing
     * the document.
     * @example Syntax
     * var element = document.elementFromAbsolutePoint(x, y);
     * @param {number} x - the X coordinate
     * @param {number} y - the Y coordinate
     * @returns {Element}
     */
    this.document.elementFromAbsolutePoint = function(x, y) {
      var elm, scrollX, scrollY, newX, newY;
      scrollX = window.pageXOffset;
      scrollY = window.pageYOffset;
      window.scrollTo(x, y);
      newX = x - window.pageXOffset;
      newY = y - window.pageYOffset;
      elm = this.elementFromPoint(newX, newY);
      if (closestFixed(elm)) {
        var newElm, display, fixedElm;
        fixedElm = closestFixed(elm);
        display = fixedElm.style.display;
        fixedElm.style.display = 'none';
        newElm = this.elementFromPoint(newX, newY);
        if (!/body|html/.test(newElm.tagName.toLowerCase())) {
          elm = newElm;
        }
        fixedElm.style.display = display;
      }
      window.scrollTo(scrollX, scrollY);
      return elm;
    };
  }).call(this);


(function(){
    function randomId(){
        let ret = "SG_"
        let possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        for(let i=0;i<25;i++) ret += possible.charAt(Math.floor(Math.random() * possible.length));
        return ret
    }

    function assignSGInfo(elem){
        elem.setAttribute("sg:id", randomId())
        elem.setAttribute("sg:rect", JSON.stringify(elem.getBoundingClientRect()))
        for(let child of elem.children) assignSGInfo(child)
    }
    
    assignSGInfo(document.body)

    function getPointData(leap_size){
        scroll(0, 0)
        let width = Math.max(document.body.scrollWidth, document.body.offsetWidth, 
            document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );
        let height = Math.max(document.body.scrollHeight, document.body.offsetHeight, 
            document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );
        let ret = []
        for(let y=0;y<height;y+=leap_size){
            ret.push([])
            for(let x=0;x<width;x+=leap_size){
                let elem = document.elementFromAbsolutePoint(x, y)
                if(elem){
                    let sg_id = elem.getAttribute("sg:id")
                    ret[y/16].push([sg_id, getComputedStyle(elem).cursor, x, y])
                }
                else ret[y/16].push([null, "auto", x, y])
            }
        }
        return ret
    }
    document.body.setAttribute('sg:point-data', JSON.stringify(getPointData(16)))
    console.log('<html>' + document.documentElement.innerHTML + '</html>')
})()