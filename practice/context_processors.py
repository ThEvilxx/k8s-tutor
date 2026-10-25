from django.conf import settings
def release(request):
    return {"app_version": settings.APP_VERSION, "llm_mode": settings.LLM_MODE}
