from datetime import datetime, timedelta

from django.views.generic import DetailView, FormView, ListView
from django.shortcuts import render_to_response
from django.db.models import Q

from braces.views import (LoginRequiredMixin, JSONResponseMixin,
                          AjaxResponseMixin)

from .models import PropertyListing
from bases.forms import RequestInformationForm


class PropertyDetailView(DetailView):   
    """
        Detail Page for the property listing page.
    """
    
    model = PropertyListing
    context_object_name = "property"
    template_name = "easyapp/rental_listing_detail.html"
    form_class = RequestInformationForm
    
    def get(self, request, *args, **kwargs):
        self.base = request.base
        self.user = request.user
        return super(PropertyDetailView, self).get(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(PropertyDetailView, self).get_context_data(**kwargs)
        if self.user.is_authenticated():
            # Display mylisting propertise in the property detailed Page.
            bookmarked_listing_ids =  UserPropertyBookmark.objects.filter(
                                  user = self.user
                                ).values_list('listing_id', flat=True)
            
            properties = PropertyListing.objects.filter(
                    listingtype='r',
                    listing_id__in = list(bookmarked_listing_ids)
                   ).order_by('-featured')
        else:
            properties = list()
        
        context['form'] = RequestInformationForm()
        context['properties'] = properties
        return context


class RequestInformationView(AjaxResponseMixin, JSONResponseMixin, FormView):
    """
        Display Request information form in the detailed listing page.
    """
    
    form_class = RequestInformationForm

    def form_invalid(self, form):
    
        json_dict = {
            'success': False,
            #'message' : [str(error.message) for error in form.errors]
            'message': "Please enter the required fields."
        }
        return self.render_json_response(json_dict)
    
    def form_valid(self, form):
        
        # If the form is valid, i will send the mail to the admin user with the filled information.
        form.send_email()
        
        json_dict = {
            'success': True,
            'message': "Message sent Successfully!"
        }
        return self.render_json_response(json_dict)


class RentalListView(ListView):
    """
    Class that handles the view of all
    rental properties of a base.
    """

    model = PropertyListing
    context_object_name = "properties"
    
    def get_queryset(self):
        return super(RentalListView,
                   self
                  ).get_queryset().filter(
                    listingtype='r',
                    market__in = get_base_markets(self.base)
                  )

    def get(self, request, *args, **kwargs):        
        self.base = request.base
        return super(RentalListView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.base = request.base
        self.object_list = self.get_queryset()
        
        # Search query
        location = request.POST["location"] #location: city, zip, street
        
        if not location.strip():
            city, zipcode, street = None, None, None
        
        else:
            try:
                city, zipcode, street = location.split(",", 2) #maxsplit - 2

            except ValueError:
                try:
                    city, zipcode = location.split(",")
                    street = None
            
                except ValueError:
                    city = location
                    zipcode = None
                    street = None            
        
        self.object_list = self.get_queryset()
        
        if city:
            query = (
                     Q(city__icontains = city.strip()) |
                     Q(zip__icontains = city.strip()) |
                     Q(address1__icontains = city.strip())
                    )

            self.object_list = self.object_list.filter(query)

        if zipcode:
            query = (
                     Q(city__icontains = zipcode.strip()) |
                     Q(zip__icontains = zipcode.strip()) |
                     Q(address1__icontains = zipcode.strip())
                    )            
            self.object_list = self.object_list.filter(query)

        if street:
            query = (
                     Q(city__icontains = street.strip()) |
                     Q(zip__icontains = street.strip()) |
                     Q(address1__icontains = street.strip())
                    )  
            self.object_list = self.object_list.filter(query)

        context = self.get_context_data(object_list=self.object_list)
        context["location"] = location
        
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(RentalListView, self).get_context_data(**kwargs)
        context['base'] = self.base
        return context


class RentalGalleryView(RentalListView):
    """
    Class that handles paginated Gallery view of all
    rental properties of a base.
    """
    
    template_name = "easyapp/rental_gallery_view.html"
    
    def get_context_data(self, **kwargs):
        context = super(RentalGalleryView, self).get_context_data(**kwargs)
        context['gallery_page'] = 'rents_gallery'
        context['map_page'] = 'rents_map'
        return context

