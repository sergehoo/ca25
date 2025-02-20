from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from administration.models import Event, Session, Attendance, Temoignage
from public.models import User, BeToBe, Meeting, Profile, Album, Photo, Category, BlogPost, Comment, GuestarsSpeaker, \
    VisitCounter


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'fonction', 'civilite', 'nom', 'prenom', 'email', 'role', 'company', 'sector')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'company', 'sector')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'fonction', 'civilite', 'nom', 'prenom', 'email', 'password')}),
        ('Informations personnelles', {'fields': ('role', 'company', 'sector', 'description', 'preferences')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'company', 'sector'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "address", "linkedin", "twitter")
    search_fields = ("user__nom", "user__prenom", "user__email")
    list_filter = ("birth_date",)
    ordering = ('user',)  # Tri des éléments
    autocomplete_fields = ('user',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location', 'organizer')
    search_fields = ('name', 'organizer__username', 'location')
    list_filter = ('start_date', 'end_date')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'start_time', 'end_time')
    search_fields = ('title', 'event__name')
    list_filter = ('start_time', 'end_time')
    readonly_fields = ('qr_code',)  # Empêcher la modification manuelle du QR Code


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'scanned_at')
    search_fields = ('user__username', 'session__title')
    list_filter = ('scanned_at',)
    ordering = ('user',)  # Tri des éléments
    autocomplete_fields = ('user',)


@admin.register(BeToBe)
class BeToBeAdmin(admin.ModelAdmin):
    """ Gestion des sessions B2B dans l'admin Django """
    list_display = ("sponsor", "date", "start_time", "end_time", "details")
    list_filter = ("date", "sponsor")
    search_fields = ("sponsor__nom", "details")
    ordering = ("date", "start_time")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """ Gestion des rencontres dans l'admin Django """
    list_display = ("participant", "btob", "confirmed_at")
    list_filter = ("btob__date", "participant")
    search_fields = ("participant__nom", "btob__sponsor__nom")
    readonly_fields = ("confirmed_at",)

    def get_queryset(self, request):
        """ Optimisation de la requête avec `select_related` pour éviter trop de requêtes SQL """
        return super().get_queryset(request).select_related("participant", "btob", "btob__sponsor")


@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'note', 'statut', 'date_soumission')
    list_filter = ('statut', 'date_soumission')
    search_fields = ('nom', 'email', 'temoignage')
    actions = ['valider_temoignage']

    def valider_temoignage(self, request, queryset):
        queryset.update(statut='Validé')
        self.message_user(request, "Les témoignages sélectionnés ont été validés.")

    valider_temoignage.short_description = "Valider les témoignages sélectionnés"


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_creation')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'image', 'date_ajout')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at')
    list_filter = ('status', 'category', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('author', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)


@admin.register(GuestarsSpeaker)
class GuestarsSpeakerAdmin(admin.ModelAdmin):
    list_display = ('user', 'fonction', 'organisme')  # Colonnes affichées dans la liste
    search_fields = ('user__nom', 'user__prenom', 'fonction', 'organisme')  # Champs de recherche
    list_filter = ('organisme',)  # Filtres à droite
    ordering = ('user',)  # Tri des éléments
    autocomplete_fields = ('user',)


@admin.register(VisitCounter)
class VisitCounterAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'timestamp', 'user_agent')

    def total_visits(self):
        return format_html("<strong>{}</strong>", VisitCounter.objects.count())

    total_visits.short_description = "Total des visites"


# Ajouter un panneau de statistiques dans l'admin
admin.site.site_header = "Administration du site"
admin.site.site_title = "Admin"
admin.site.index_title = f"Total des visites : {VisitCounter.objects.count()}"
