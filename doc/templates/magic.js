/*
 * magic.js — makes rationales in the HTML-ified spec collapsible.
 *
 * Copyright © 2010 Collabora Ltd.
 * Copyright © 2010 Nokia Corporation.
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2.1 of the License, or (at
 * your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
 * for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * Author: Will Thompson <will.thompson@collabora.co.uk>
 */

$(document).ready(main);

function toggleRationale() {
  /* Slide the rationale body open or closed */
  $(this).next().slideToggle('fast');

  /* Rotate the triangle */
  $(this).children('span.ui-icon').toggleClass(
    'ui-icon-triangle-1-s ui-icon-triangle-1-e');
}

function main() {
  h5s = $('.rationale h5')

  /* Un-hide the rationale headers */
  h5s.css('display', 'block');

  /* Add a "collapsed" triangle beside all the headers, and collapse them all.
   */
  h5s.prepend("<span class='ui-icon ui-icon-triangle-1-e'/>");
  h5s.next().hide();

  h5s.click(toggleRationale);
}
