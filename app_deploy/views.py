import subprocess
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from app_user.utils import requiredLogin

# Create your views here.
@requiredLogin
def indexDeploy(requset: HttpRequest):
    return render(requset, 'deploy/index.html')

def deploy(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'deployed': False, 'message': 'Method not allowed'})
        
        subprocess.Popen(["sudo", "reboot"])
        returnData = {
            'deployed': True,
            'message': 'Deploy success'
        }
        return JsonResponse(returnData)
    except Exception as e:
        print(e)
        returnData = {
            'deployed': False,
            'message': str(e)
        }
        return JsonResponse(returnData)