from django.shortcuts import render, redirect
from django.views import View
from ..models import Part, Part_stock, User
from common.constants import Add_to_stock_process_type, Remove_from_stock_process_type
from django_serverside_datatable.views import ServerSideDatatableView


class Parts(View):
    def get(self, request):
        user_id = request.session["user_id"]
        # If the user session is ended, then the user should log in again
        if user_id is None:
            return redirect("/login/")

        user = User.objects.filter(id=user_id).first()
        # If the user information doesn't exist in DB, then go to the login page to check user data again
        if user is None:
            request.session["user_id"] = None
            return redirect("/login")

        # Retrieve only the parts that the user can update stock information on it
        available_parts_with_stocks = Part_stock.objects.filter(
            part__team_id=user.team_id
        ).order_by("part__name")

        data = {"available_parts_with_stocks": available_parts_with_stocks}
        return render(request, "parts/index.html", data)

    def post(self, request):
        part_stock_id = request.POST.get("part_stock_id")
        part_stock = Part_stock.objects.filter(id=part_stock_id).first()
        # If the part doesn't exist on DB
        if part_stock is None:
            return redirect("/parts/")

        try:
            # Check stock process type. It can be add or rermove
            stock_process_type = request.POST.get("stock_process_type")
            # If the process type is add, then add parts to the stocks by added amount
            if stock_process_type == Add_to_stock_process_type:
                amount_added = request.POST.get("amount_added")
                part_stock.count += int(amount_added) or 0
                part_stock.save()
            # If process type is remove, then remove the parts from the stocks by amount
            elif stock_process_type == Remove_from_stock_process_type:
                amount_removed = request.POST.get("amount_removed")
                part_stock.count -= int(amount_removed) or 0
                # Stock count can't be lower than 0
                if part_stock.count < 0:
                    part_stock.count = 0

                part_stock.save()
        except Exception as error:
            print("An error occurred while adding/removing a part", error)

        return redirect("/parts/")


class PartListView(ServerSideDatatableView):
    queryset = Part_stock.objects.all().order_by("part__name")
    columns = ["part__name", "part__description", "part__aircraft__name", "count"]