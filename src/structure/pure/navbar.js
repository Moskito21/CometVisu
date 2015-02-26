/* navbar.js (c) 2012 by Christian Mayer [CometVisu at ChristianMayer dot de]
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
 */

define( ['_common'], function( design ) {
   var 
     basicdesign     = design.basicdesign,
     isNotSubscribed = true,
     navbarTop       = '',
     navbarLeft      = '',
     navbarRight     = '',
     navbarBottom    = '',
     $navbarLeftSize  = $( '#navbarLeft'  ).data('size'),
     $navbarRightSize = $( '#navbarRight' ).data('size');
 
design.basicdesign.addCreator('navbar', {
  create: function( navbar, path, flavour, type ) {
    var $n = $(navbar);
    var childs = $n.children();
    var id = path.split('_'); id.pop();
    var position = $n.attr('position') || 'left';
    var scope = $n.attr('scope') || -1;
    if( $n.attr('flavour') ) flavour = $n.attr('flavour');// sub design choice
    var flavourClass = flavour ? ( ' flavour_' + flavour ) : '';
    var container = '<div class="navbar clearfix' + flavourClass + '" id="' + id.join('_')+'_'+ position + '_navbar">';
    if( $n.attr('name') ) container += '<h2>' + $n.attr('name') + '</h2>';
    $( childs ).each( function(i){
      container += templateEngine.create_pages( childs[i], path + '_' + i, flavour );
    } );
    container+='</div>';
    //$container.data('scope',scope); ???
    
    var dynamic  = $n.attr('dynamic') == 'true' ? true : false;
  
    var size = $n.attr('width') || 300;
    switch( position )
    {
      case 'top':
        navbarTop += container;
        break;
        
      case 'left':
        navbarLeft += container;
        var thisSize = $navbarLeftSize || size; // FIXME - only a temporal solution
        if( dynamic ) templateEngine.pagePartsHandler.navbarSetSize( 'left', thisSize );
        break;
        
      case 'right':
        navbarRight += container;
        var thisSize = $navbarRightSize || size; // FIXME - only a temporal solution
        if( dynamic ) templateEngine.pagePartsHandler.navbarSetSize( 'right', thisSize );
        break;
        
      case 'bottom':
        navbarBottom += container;
        break;
    }
    templateEngine.pagePartsHandler.navbars[position].dynamic |= dynamic;
    
    if( isNotSubscribed )
    {
      isNotSubscribed = false;
      templateEngine.postDOMSetupFns.push( function(){
        if( navbarTop    ) $( '#navbarTop'    ).append( navbarTop    );
        if( navbarLeft   ) $( '#navbarLeft'   ).append( navbarLeft   );
        if( navbarRight  ) $( '#navbarRight'  ).append( navbarRight  );
        if( navbarBottom ) $( '#navbarBottom' ).append( navbarBottom );
      });
    }
    
    return '';
  }
});

}); // end define