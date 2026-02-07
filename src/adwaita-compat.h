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
#if __has_include(<adwaita.h>)
#include <adwaita.h>
#else

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
#define ADW_TYPE_ALERT_DIALOG GTK_TYPE_DIALOG

#define ADW_DIALOG(obj) (GTK_WIDGET(obj))
#define ADW_BANNER(obj) (GTK_WIDGET(obj))
#define ADW_PREFERENCES_GROUP(obj) (GTK_WIDGET(obj))
#define ADW_ALERT_DIALOG(obj) (GTK_DIALOG(obj))

/* Stubs for common adwaita helpers used throughout the codebase. */
static inline AdwAlertDialog *
adw_alert_dialog_new (const char *title, ...)
{
    (void) title;
    return GTK_WIDGET(gtk_dialog_new ());
}

static inline void
adw_alert_dialog_set_extra_child (AdwAlertDialog *d, GtkWidget *child)
{
    GtkWidget *content_area = gtk_dialog_get_content_area (GTK_DIALOG (d));
    if (content_area && GTK_IS_WIDGET (child)) {
        gtk_container_add (GTK_CONTAINER (content_area), child);
        gtk_widget_show (child);
    }
}

static inline void
adw_alert_dialog_add_response (AdwAlertDialog *d, const char *response_id, const char *label)
{
    (void) d; (void) response_id; (void) label;
}

static inline void
adw_alert_dialog_add_responses (AdwAlertDialog *d, ...)
{
    (void) d;
}

static inline void
adw_alert_dialog_set_body (AdwAlertDialog *d, const char *body)
{
    (void) d; (void) body;
}

static inline void
adw_alert_dialog_set_body_use_markup (AdwAlertDialog *d, gboolean use_markup)
{
    (void) d; (void) use_markup;
}

static inline void
adw_alert_dialog_set_heading (AdwAlertDialog *d, const char *heading)
{
    (void) d; (void) heading;
}

static inline void
adw_alert_dialog_set_close_response (AdwAlertDialog *d, const char *response_id)
{
    (void) d; (void) response_id;
}

static inline void
adw_alert_dialog_set_response_enabled (AdwAlertDialog *d, const char *response_id, gboolean enabled)
{
    (void) d; (void) response_id; (void) enabled;
}

static inline void
adw_alert_dialog_set_response_appearance (AdwAlertDialog *d, const char *response_id, int appearance)
{
    (void) d; (void) response_id; (void) appearance;
}

static inline void
adw_alert_dialog_choose (AdwAlertDialog *d, GtkWidget *parent, GCancellable *cancellable, GAsyncReadyCallback callback, gpointer user_data)
{
    (void) d; (void) parent; (void) cancellable; (void) callback; (void) user_data;
}

static inline const char *
adw_alert_dialog_choose_finish (AdwAlertDialog *d, GAsyncResult *result)
{
    (void) d; (void) result;
    return NULL;
}

static inline void
adw_dialog_present (AdwDialog *d, GtkWidget *parent)
{
    (void) parent;
    if (GTK_IS_WIDGET (d))
        gtk_widget_show (GTK_WIDGET (d));
}

static inline void
adw_dialog_force_close (AdwDialog *d)
{
    if (GTK_IS_WIDGET (d))
        gtk_widget_destroy (GTK_WIDGET (d));
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

#endif /* HAVE_LIBADWAITA */

#endif /* ADWAITA_COMPAT_H */
