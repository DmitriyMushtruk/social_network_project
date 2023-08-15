from rest_framework import permissions
from .models import Page

# class CanViewPrivatePage(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False  # Unauthorized users cannot see pages

#         page_name = view.kwargs.get('page_name')
#         selected_page_id = request.session.get('selected_page_id') # Тут сохраняем выбранную польщователем страницу
#         current_page = Page.objects.filter(name=page_name).first()

#         if selected_page_id is None:
#             return False  # The user has not selected a self page

#         if not current_page:
#             return False  # Page not found

#         if not current_page.is_private:
#             return True  # Public pages can be seen by everyone

#         return current_page.followers.filter(name=selected_page_id).exists()
    
    # Вот тут вопрос. Пользователь залогинился, выбрал страницу из списка своих страниц,
    # подписался на приватную страницу (владелец принял запрос юзера на подписку)
    # потом этот юзер свапнул страницу на другую, и у него уже нету доступа к той приватной странице
    # а я тут делаю проверку на user.id...
    # Надо проверить есть ли юзер is_authenticated, но в то же время проверить 
    # подписана ли страница через которую сидит юзер на ту страницу которую он хочет посмотреть
    # 
    # Сейчас если страница приватная то у меня нету прав ее смотреть.
    # Есть вариант сохранять в сессии инфу о том какую страницу юзер выбрал после авторизации
    # но это уже на стороне фронта, так как писать эти permissions?

class CanDeletePostPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.has_perm('page.delete_post'):
            return True
        
        if request.user == view.get_object().page.owner:
            return True
        
        user_role = request.user.role
        if user_role in ['moderator', 'admin']:
            return True
        
        return False