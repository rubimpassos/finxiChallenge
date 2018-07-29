def notifications(request):
    context = {}
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.unread()
        if unread_notifications.exists():
            context['notifications'] = unread_notifications

    return context
