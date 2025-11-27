from django.urls import path

from app_user.views import user_views as user_views
from app_user.views import setting_user_views as setting__user_views
from app_user.views import immigration_views as immigration_views
from app_user.views import setting_opd_views as setting_opd_views
from app_user.views import opd_views as opd_views




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
    path('opdsetting/budget/', view=setting_opd_views.budgetOpd, name='buggetSettingOpd'),
    path('opdsetting/budget/add/', view=setting_opd_views.addBudgetOpd, name='addBudgetOpd'),
    path('opdsetting/budget/edit/', view=setting_opd_views.editBudgetOpd, name='editBudgetOpd'),
    path('opdsetting/budget/delete/<str:id>/', view=setting_opd_views.deleteBudgetOpd, name='deleteBudgetOpd'),
    path('opdsetting/budget/api/filter/<str:type>', view=setting_opd_views.filterBudgetOpd, name='filterBudgetOpd'),
    path('opdsetting/budget/api/get/<str:id>/', view=setting_opd_views.getBudgetOpd, name='getBudgetOpd'),
    path('opdsetting/option/', view=setting_opd_views.optionOpd, name='optionSettingOpd'),
    path('opdsetting/option/add/', view=setting_opd_views.addOptionOpd, name='addOptionOpd'),
    path('opdsetting/option/edit/', view=setting_opd_views.editOptionOpd, name='editOptionOpd'),
    path('opdsetting/option/delete/<str:id>/', view=setting_opd_views.deleteOptionOpd, name='deleteOptionOpd'),
    path('opdsetting/option/api/filter/', view=setting_opd_views.filterOptionOpd, name='filterOptionOpd'),
    path('opdsetting/option/api/get/<str:id>/', view=setting_opd_views.getOptionOpd, name='getOptionOpd'),
]
