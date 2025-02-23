from django.templatetags.static import static


def open_graph_image(request):
    """ Context processor pour générer l'URL complète de l'image Open Graph """
    og_image = request.build_absolute_uri(static("assets/cavisuel.webp")).replace("//static", "/static")
    return {"og_image": og_image}
