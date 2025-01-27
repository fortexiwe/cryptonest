"""
URL configuration for cloudarchive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from regauth.views import main_page, guest_page, auth_page, reg_page, deauth, create_folder, folder, confirm_email, buy_GB
from files.views import upload_file, download_file, cache_info, delete_file, transfer_file, plus_size, get_size, rename_file, download_selected_files
from AI.views import image
from blockchain.views import blockchain_page, store_view, buy_card, mining_simulator, start_mining, stop_mining, marketplace, create_order, fulfill_order, get_candlestick_data
from settings.views import settings
from regauth.views import custom_404
from django.conf.urls import handler404

handler404 = 'regauth.views.custom_404'


urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),
    
    # Authentication and main pages
    path('', main_page, name='main_page'),
    path('guest/', guest_page, name='guest_page'),
    path('auth/', auth_page, name='auth_page'),
    path('reg/', reg_page, name='reg_page'),
    path('deauth/', deauth, name='deauth'),
    path('create_folder/', create_folder, name='create_folder'),
    path('folder/<uuid:folder_id>/', folder, name='folder'),
    path('confirm-email/', confirm_email, name='confirm_email'),
    path('buy_GB/', buy_GB, name='buy_GB'),
    
    # File management URLs
    path('load_file/', upload_file, name='load_file'),
    path('download/<int:file_id>/', download_file, name='download_file'),
    path('cache_info/', cache_info, name='cache_info_page'),
    path('delete/<int:file_id>/', delete_file, name='delete_file'),
    path('settings/', settings, name='settings'),
    path('transfer/', transfer_file, name='transfer'),
    path('plus_size/', plus_size, name='size'),
    path('get_size/', get_size, name='get_size'),
    path('rename/', rename_file, name='rename'),
    path('download_more/', download_selected_files, name='download_more'),

    # AI
    path('generate_image/', image, name='generate_image'),

    # Blockchain
    path('blockchain/', blockchain_page, name='blockchain'),
    path('store/', store_view),
    path('buy_card/<str:name>', buy_card, name='buy_card'),
    path('mining/', mining_simulator, name='mining'),
    path('start_mining/', start_mining, name='start_mining'),
    path('stop_mining/', stop_mining, name='stop_mining'),
    path('exchange/', marketplace, name='marketplace'),
    path('create_order/', create_order, name='create_order'),
    path('fulfill_order/<int:order_id>/', fulfill_order, name='fulfill_order'),
    path('api/candlestick-data/', get_candlestick_data, name='candlestick_data'),
]
