
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect
from .models import Activity
from .serializers import ActivitySerializer
from .permissions import IsOwner

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['activity_type', 'date']
    ordering_fields = ['date', 'duration', 'calories_burned', 'distance']
    ordering = ['-date']

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def history(self, request):
        activities = self.get_queryset()

        # Filter by activity type if provided
        activity_type = request.query_params.get('activity_type', None)
        if activity_type:
            activities = activities.filter(activity_type=activity_type)

        # Filter by date range if provided
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            activities = activities.filter(date__gte=start_date)
        if end_date:
            activities = activities.filter(date__lte=end_date)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        period = request.query_params.get('period', 'week')  # week, month, or all
        activities = self.get_queryset()

        # Filter by period
        if period == 'week':
            start_date = timezone.now() - timedelta(days=7)
            activities = activities.filter(date__gte=start_date)
        elif period == 'month':
            start_date = timezone.now() - timedelta(days=30)
            activities = activities.filter(date__gte=start_date)

        # Calculate metrics
        total_duration = activities.aggregate(Sum('duration'))['duration__sum'] or 0
        total_distance = activities.aggregate(Sum('distance'))['distance__sum'] or 0
        total_calories = activities.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
        avg_duration = activities.aggregate(Avg('duration'))['duration__avg'] or 0
        avg_distance = activities.aggregate(Avg('distance'))['distance__avg'] or 0
        avg_calories = activities.aggregate(Avg('calories_burned'))['calories_burned__avg'] or 0

        # Activity type distribution
        activity_distribution = activities.values('activity_type').annotate(
            count=Count('id'),
            total_duration=Sum('duration'),
            total_distance=Sum('distance'),
            total_calories=Sum('calories_burned')
        )

        return Response({
            'total_duration': total_duration,
            'total_distance': total_distance,
            'total_calories': total_calories,
            'avg_duration': avg_duration,
            'avg_distance': avg_distance,
            'avg_calories': avg_calories,
            'activity_distribution': activity_distribution,
            'period': period
        })

# Web views for HTML templates
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'activities/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 10

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by('-date')

class ActivityCreateView(LoginRequiredMixin, CreateView):
    model = Activity
    template_name = 'activities/activity_form.html'
    fields = ['activity_type', 'duration', 'distance', 'calories_burned', 'date', 'notes']
    success_url = reverse_lazy('activity_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Activity created successfully!')
        return super().form_valid(form)

class ActivityUpdateView(LoginRequiredMixin, UpdateView):
    model = Activity
    template_name = 'activities/activity_form.html'
    fields = ['activity_type', 'duration', 'distance', 'calories_burned', 'date', 'notes']
    success_url = reverse_lazy('activity_list')

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Activity updated successfully!')
        return super().form_valid(form)

class ActivityDeleteView(LoginRequiredMixin, DeleteView):
    model = Activity
    template_name = 'activities/activity_confirm_delete.html'
    success_url = reverse_lazy('activity_list')

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Activity deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ActivityHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'activities/activity_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = Activity.objects.filter(user=self.request.user).order_by('-date')

        # Apply filters
        activity_type = self.request.GET.get('activity_type')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if activity_type:
            activities = activities.filter(activity_type=activity_type)
        if start_date:
            activities = activities.filter(date__gte=start_date)
        if end_date:
            activities = activities.filter(date__lte=end_date)

        # Calculate totals
        total_duration = activities.aggregate(Sum('duration'))['duration__sum'] or 0
        total_calories = activities.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0

        context['activities'] = activities
        context['total_duration'] = total_duration
        context['total_calories'] = total_calories
        return context
