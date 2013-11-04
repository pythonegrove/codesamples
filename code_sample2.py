from django.views.generic import ListView

from braces.views import JSONResponseMixin

from .models import MenuItem


class TopMenuListView(JSONResponseMixin, ListView):
    """
    AJAX callable JSON listing of Menus of a base.
    """
    model = MenuItem

    def get_queryset(self):
        return super(TopMenuListView,
                     self
                    ).get_queryset().filter(
                      base=self.base
                    ).order_by(
                      "category__order",
                      "order"
                    ).values(
                      "category__category_name",
                      "item_name",
                      "url"
                    )

    def get(self, request, *args, **kwargs):
        self.base = request.base

        menu_list = self.get_queryset()
        
        # Convert queryset into a hierarchial dictionary
        # of menu categories and menu items.
        response = {}
        for menu in menu_list:
            if response.has_key(menu["category__category_name"]):
                response[menu["category__category_name"]].append(menu)
            
            else:
                response[menu["category__category_name"]] = [menu]
            
        return self.render_json_response(response)

