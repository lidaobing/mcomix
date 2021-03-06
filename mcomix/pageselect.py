"""pageselect.py - The dialog window for the page selector."""

import gtk

class Pageselector(gtk.Dialog):

    """The Pageselector takes care of the popup page selector
    """

    def __init__(self, window):
        self._window = window
        self._page_selector_dialog = gtk.Dialog.__init__(self, "Go to page...", window,
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.add_buttons(_('_Go'), gtk.RESPONSE_OK,
                         _('_Cancel'), gtk.RESPONSE_CANCEL,)
        self.set_default_response(gtk.RESPONSE_OK)
        self.set_has_separator(False)
        self.connect('response', self._response)
        self.set_resizable(True)

        # Start thumbnail generation in case it has been delayed
        self._window.thumbnailsidebar.load_thumbnails(True)
        self._window.thumbnailsidebar.thumbnail_loaded += self._thumbnail_loaded

        self._number_of_pages = self._window.imagehandler.get_number_of_pages()

        self._selector_adjustment = gtk.Adjustment(value=self._window.imagehandler.get_current_page(),
                              lower=1,upper=self._number_of_pages,
                              step_incr=1, page_incr=1 )

        self._selector_adjustment.connect( 'value-changed', self._cb_value_changed )

        self._page_selector = gtk.VScale(self._selector_adjustment)
        self._page_selector.set_draw_value(False)
        self._page_selector.set_digits( 0 )

        self._page_spinner = gtk.SpinButton(self._selector_adjustment)
        self._page_spinner.connect( 'changed', self._page_text_changed )
        self._page_spinner.set_activates_default(True)
        self._page_spinner.set_numeric(True)
        self._pages_label = gtk.Label(_(' of %s') % self._number_of_pages)
        self._pages_label.set_alignment(0, 0.5)

        self._image_preview = gtk.Image()
        self._set_thumbnail(int(self._selector_adjustment.value) - 1)

        # Group preview image and page selector next to each other
        preview_box = gtk.HBox()
        preview_box.set_border_width(5)
        preview_box.set_spacing(5)
        preview_box.pack_start(self._image_preview, True)
        preview_box.pack_end(self._page_selector, False)
        # Below them, group selection spinner and current page label
        selection_box = gtk.HBox()
        selection_box.set_border_width(5)
        selection_box.pack_start(self._page_spinner, True)
        selection_box.pack_end(self._pages_label, False)

        self.get_content_area().pack_start(preview_box, True)
        self.get_content_area().pack_end(selection_box, False)
        self.show_all()

        # Set focus on the input box.
        self._page_spinner.select_region(0, -1)
        self._page_spinner.grab_focus()

    def _cb_value_changed(self, *args):
        """ Called whenever the spinbox value changes. Updates the preview thumbnail. """
        self._set_thumbnail(int(self._selector_adjustment.value) - 1)

    def _page_text_changed(self, control, *args):
        """ Called when the page selector has been changed. Used to instantly update
            the preview thumbnail when entering page numbers by hand. """
        if control.get_text().isdigit():
            page = int(control.get_text())
            if page > 0 and page <= self._number_of_pages:
                control.set_value(page)

    def _response(self, widget, event, *args):
        if event == gtk.RESPONSE_OK:
            self._window.set_page(int(self._selector_adjustment.value))

        self.destroy()

    def _set_thumbnail(self, page):
        """ Set the preview thumbnail for the page selector.
        If a thumbnail isn't cached yet, use a transparent image. """

        pixbuf = self._window.thumbnailsidebar.get_thumbnail(page + 1)
        self._image_preview.set_from_pixbuf(pixbuf)

    def _thumbnail_loaded(self, page, pixbuf):
        """ Since it cannot be guaranteed that thumbnails have already
        been loaded for the currently selected page, this callback
        re-loads the current thumbnail when it becomes available. """

        if page == int(self._selector_adjustment.value):
            self._set_thumbnail(page - 1)

# vim: expandtab:sw=4:ts=4
