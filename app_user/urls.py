from django.urls import path

from app_user.views import user_views as user_views
from app_user.views import setting_user_views as setting__user_views
from app_user.views import immigration_views as immigration_views
from app_user.views import setting_opd_views as setting_opd_views
from app_user.views import opd_views as opd_views
from app_user.views import family_views as family_views
from app_user.views import report_opd_views as report_opd_views






urlpatterns = [
    path('', view=user_views.index, name='indexUser'),
    path('add/', view=user_views.addUser, name='addUser'),
    path('edit/<str:id>/', view=user_views.editUser, name='editUser'),
    path('delete/<str:id>/', view=user_views.deleteUser, name='deleteUser'),
    path('regisuser/<str:id>/', view=user_views.regisUser, name='regisUser'),
    path('repass/<str:id>/', view=user_views.resetPassword, name='rePassUser'),
    path('api/list/', view=user_views.listUser, name='listUser'),
    path('alien/', view= user_views.AddAlienUser, name= 'AddAlienUser'),
    # -----------------------------------------------------
    # ------------------- setting user --------------------
    # -----------------------------------------------------
    path('setting/', view=setting__user_views.indexSettingUser, name= 'indexSettingUser'),
    path('setting/add/', view=setting__user_views.addSettingUser, name= 'addSettingUser'),
    path('setting/edit/<str:id>/', view=setting__user_views.editSettingUser, name= 'editSettingUser'),
    path('setting/delete/<str:id>/', view=setting__user_views.deleteSettingUser, name= 'deleteSettingUser'),
    path('setting/import/', view=setting__user_views.importSettingUser, name= 'importSettingUser'),
    path('setting/template/', view=setting__user_views.exportExcelTemplate, name= 'userExcelTemplate'),
    # -----------------------------------------------------
    # ------------------- immigration --------------------
    # -----------------------------------------------------
    path('immigration/', view=immigration_views.index, name='indexImmigration'),
    path('immigration/addjson/', view=immigration_views.addJson, name='addJson'),
    path('immigration/editjson/', view=immigration_views.editJson, name='editJson'),
    path('immigration/deletejson/<str:id>/', view=immigration_views.deleteJson, name='deleteJson'),
    path('immigration/api/listjson/', view=immigration_views.listImmigrationJson, name='listImmigrationJson'),
    path('immigration/api/getjson/<str:id>/', view=immigration_views.getImmigrationJson, name='getImmigrationJson'),
    # -----------------------------------------------------
    # -------------------- OPD System ---------------------
    # -----------------------------------------------------
    path('opd/', view=opd_views.index, name='indexOpd'),
    path('opd/history/<str:id>/', view=opd_views.historyOpd, name='historyOpd'),
    path('opd/list/', view=opd_views.listPageOpd, name='listOpd'),
    path('opd/api/filter/', view=opd_views.filterSearchOpd, name='filterSearchOpd'),
    path('opd/add/<str:id>/', view=opd_views.addOpd, name="addOpd"),
    path('opd/api/add/', view=opd_views.addOpdJson, name='addOpdJson'),
    path('opd/edit/<str:id>/', view=opd_views.editOpd, name="editOpd"),
    path('opd/api/edit/', view=opd_views.editOpdJson, name='editOpdJson'),
    path('opd/api/delete/<str:id>/', view=opd_views.deleteOpdJson, name='deleteOpdJson'),
    path('opdsetting/budget/', view=setting_opd_views.budgetOpd, name='buggetSettingOpd'),
    path('opdsetting/budget/add/', view=setting_opd_views.addBudgetOpd, name='addBudgetOpd'),
    path('opdsetting/budget/edit/', view=setting_opd_views.editBudgetOpd, name='editBudgetOpd'),
    path('opdsetting/budget/delete/<str:id>/', view=setting_opd_views.deleteBudgetOpd, name='deleteBudgetOpd'),
    path('opdsetting/budget/api/filter/<str:type>', view=setting_opd_views.filterBudgetOpd, name='filterBudgetOpd'),
    path('opdsetting/budget/api/get/<str:id>/', view=setting_opd_views.getBudgetOpd, name='getBudgetOpd'),
    path('opdsetting/specialbudget/add/', view=setting_opd_views.addSpecialBudgetOpd, name='addSpecialBudgetOpd'),
    path('opdsetting/specialbudget/edit/', view=setting_opd_views.editSpecialBudgetOpd, name='editSpecialBudgetOpd'),
    path('opdsetting/specialbudget/delete/<str:id>/', view=setting_opd_views.deleteSpecialBudgetOpd, name='deleteSpecialBudgetOpd'),
    path('opdsetting/specialbudget/api/filter/', view=setting_opd_views.filterSpecialBudgetOpd, name='filterSpecialBudgetOpd'),
    path('opdsetting/specialbudget/api/get/<str:id>/', view=setting_opd_views.getSpecialBudgetOpd, name='getSpecialBudgetOpd'),
    path('opdsetting/option/', view=setting_opd_views.optionOpd, name='optionSettingOpd'),
    path('opdsetting/option/add/', view=setting_opd_views.addOptionOpd, name='addOptionOpd'),
    path('opdsetting/option/edit/', view=setting_opd_views.editOptionOpd, name='editOptionOpd'),
    path('opdsetting/option/delete/<str:id>/', view=setting_opd_views.deleteOptionOpd, name='deleteOptionOpd'),
    path('opdsetting/option/api/filter/', view=setting_opd_views.filterOptionOpd, name='filterOptionOpd'),
    path('opdsetting/option/api/get/<str:id>/', view=setting_opd_views.getOptionOpd, name='getOptionOpd'),
    # ------------------------------------------------------------
    # -------------------- Report OPD System ---------------------
    # ------------------------------------------------------------
    path('report/opd/', view=report_opd_views.index, name='indexReportOpd'),
    path('report/opd/api/piechart/', view=report_opd_views.pieChart, name='pieChart'),
    path('report/opd/export/', view=report_opd_views.exportReportOPD, name='exportReportOPD'),
    # -----------------------------------------------------
    # ------------------- Family System -------------------
    # -----------------------------------------------------
    path('family/', view=family_views.index, name='indexFamily'),
    path('family/add/', view=family_views.add, name='addFamily'),
    path('family/api/add/', view=family_views.addJson, name='addJsonFamily'),
    path('family/edit/<str:id>/', view= family_views.edit,name="editFamily"),
    path('family/api/edit/', view=family_views.editJson, name='editJsonFamily'),
    path('family/api/delete/<str:id>', view=family_views.deleteJson, name='deleteJsonFamily'),
]
