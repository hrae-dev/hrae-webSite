from django.shortcuts import render

# Main pages
def index(request):
    return render(request, 'Home/index.html')

def about_us(request):
    return render(request, 'Home/about_us.html')

def our_services(request):
    return render(request, 'Home/services.html')

def our_team(request):
    return render(request, 'Home/our_team.html')

def news(request):
    return render(request, 'Home/news.html')

def health_campaigns(request):
    return render(request, 'Home/health_campaigns.html')

def our_partners(request):
    return render(request, 'Home/our_partners.html')

def practical_info(request):
    return render(request, 'Home/practical_info.html')

def contact_us(request):
    return render(request, 'Home/contact.html')

# Detail pages
def service_detail(request, service_id):
    return render(request, 'services/service_detail.html', {'service_id': service_id})

def doctor_detail(request, doctor_id):
    return render(request, 'doctors/doctor_detail.html', {'doctor_id': doctor_id})

def news_detail(request, news_id):
    return render(request, 'news/news_detail.html', {'news_id': news_id})

def campaign_detail(request, campaign_id):
    return render(request, 'campaigns/campaign_detail.html', {'campaign_id': campaign_id})
