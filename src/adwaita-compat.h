/* Minimal compatibility header to allow building without libadwaita
 * for GTK3/Cinnamon ports. This provides lightweight typedefs and
 * stub functions for Adwaita types used across the codebase.
 *
 * NOTE: This is intentionally small and only intended to help compilation
 * while porting. It does not implement full libadwaita behavior.
 */

#ifndef ADWAITA_COMPAT_H
#define ADWAITA_COMPAT_H

#include <glib.h>
#include <gtk/gtk.h>

/* If libadwaita is actually available, prefer it. */
#if defined(__has_include)
#  if __has_include(<adwaita.h>)
#    include <adwaita.h>
#    if !defined(HAVE_LIBADWAITA)
#      define HAVE_LIBADWAITA 1
#    endif
#  else
#    define ADWAITA_COMPAT_FALLBACK 1
#  endif
#elif defined(HAVE_LIBADWAITA)
#  include <adwaita.h>
#else
#  define ADWAITA_COMPAT_FALLBACK 1
#endif

#ifdef ADWAITA_COMPAT_FALLBACK

/* Lightweight type aliases so existing code compiles */
typedef GtkWidget AdwDialog;
typedef GtkWidget AdwBanner;
typedef GtkWidget AdwActionRow;
typedef GtkWidget AdwNavigationView;
typedef GtkWidget AdwNavigationPage;
typedef GtkWidget AdwPreferencesGroup;
typedef GtkWidget AdwPreferencesDialog;
typedef GtkWidget AdwToast;
typedef GtkWidget AdwCarousel;
typedef GtkWidget AdwSpinner;
typedef GtkWidget AdwBin;
typedef GtkWidget AdwClamp;
typedef GtkWidget AdwHeaderBar;
typedef GtkWidget AdwWindowTitle;
typedef GtkWidget AdwAlertDialog;
typedef GtkWidget AdwToolbarView;
typedef GtkWidget AdwStatusPage;

typedef int AdwNavigationDirection;
#define ADW_NAVIGATION_DIRECTION_FORWARD 1
#define ADW_NAVIGATION_DIRECTION_BACK 0

/* Minimal type macros for casts */
#define ADW_TYPE_DIALOG GTK_TYPE_WIDGET
#define ADW_TYPE_BIN GTK_TYPE_WIDGET
#define ADW_TYPE_PREFERENCES_DIALOG GTK_TYPE_WIDGET
#define ADW_TYPE_PREFERENCES_GROUP GTK_TYPE_WIDGET

#define ADW_DIALOG(obj) (GTK_WIDGET(obj))
#define ADW_BANNER(obj) (GTK_WIDGET(obj))
#define ADW_PREFERENCES_GROUP(obj) (GTK_WIDGET(obj))

/* Stubs for common adwaita helpers used throughout the codebase. */
static inline AdwAlertDialog *
adw_alert_dialog_new (const char *title, ...)
{
    (void) title;
    return GTK_WIDGET(gtk_window_new ());
}

static inline void
adw_alert_dialog_set_extra_child (AdwAlertDialog *d, GtkWidget *child)
{
    if (GTK_IS_WINDOW (d) && GTK_IS_WIDGET (child))
        gtk_window_set_child (GTK_WINDOW (d), child);
}

static inline void
adw_alert_dialog_add_response (AdwAlertDialog *d, int response_id, const char *label)
{
    (void) d; (void) response_id; (void) label;
}

static inline void
adw_dialog_present (AdwDialog *d, GtkWidget *parent)
{
    (void) parent;
    if (GTK_IS_WIDGET (d))
        gtk_widget_set_visible (GTK_WIDGET (d), TRUE);
}

static inline void
adw_dialog_force_close (AdwDialog *d)
{
    if (GTK_IS_WINDOW (d))
        gtk_window_destroy (GTK_WINDOW (d));
}

static inline AdwBanner *
adw_banner_new (const char *title)
{
    return GTK_WIDGET (gtk_label_new (title));
}

static inline void
adw_banner_set_title (AdwBanner *b, const char *title)
{
    if (GTK_IS_LABEL (b))
        gtk_label_set_text (GTK_LABEL (b), title ? title : "");
}

static inline void
adw_banner_set_button_label (AdwBanner *b, const char *label)
{
    (void) b; (void) label;
}

static inline void
adw_banner_set_revealed (AdwBanner *b, gboolean revealed)
{
    (void) b; (void) revealed;
}

/* Navigation view helpers */
static inline void
adw_navigation_view_push (AdwNavigationView *v, AdwNavigationPage *p)
{
    (void) v; (void) p;
}

static inline void
adw_navigation_view_push_by_tag (AdwNavigationView *v, const char *tag)
{
    (void) v; (void) tag;
}

/* Carousel stubs */
static inline void
adw_carousel_append (AdwCarousel *c, GtkWidget *w)
{
    (void) c; (void) w;
}

static inline void
adw_carousel_scroll_to (AdwCarousel *c, GtkWidget *w, gboolean anim)
{
    (void) c; (void) w; (void) anim;
}

static inline void
adw_carousel_set_allow_scroll_wheel (AdwCarousel *c, gboolean allow)
{
    (void) c; (void) allow;
}

/* Style manager stubs used for dark/light detection */
typedef struct _AdwStyleManager AdwStyleManager;
static inline AdwStyleManager*
adw_style_manager_get_default (void)
{
    return NULL;
}

static inline AdwStyleManager*
adw_style_manager_get_for_display (GdkDisplay *display)
{
    (void) display; return NULL;
}

static inline gboolean
adw_style_manager_get_dark (AdwStyleManager *m)
{
    (void) m; return FALSE;
}

#endif /* ADWAITA_COMPAT_FALLBACK */

#endif /* ADWAITA_COMPAT_H */
