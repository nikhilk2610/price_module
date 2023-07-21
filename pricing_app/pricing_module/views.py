import datetime
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import PricingConfig, ActionLog
from .serializers import PricingConfigSerializer, ActionLogSerializer


class PricingConfigListCreateView(generics.ListCreateAPIView):
    serializer_class = PricingConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PricingConfig.objects.all()

    def perform_create(self, serializer):
        day = serializer.validated_data.get('day')
        is_active = serializer.validated_data.get('is_active')

        if PricingConfig.objects.filter(day=day, is_active=is_active).exists():
            if is_active:
                raise ValidationError(
                    {'is_active': f'There is already an active=True instance with day={day}.'}
                )
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

        action_log = ActionLog.objects.create(
            user=self.request.user,
            action_type='create',
            model_name='PricingConfig',
            record_id=serializer.instance.pk,
            old_data={},
            new_data=serializer.data
        )


class PricingConfigRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PricingConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(PricingConfig, pk=pk)

    def retrieve(self, request, *args, **kwargs):
        price_config = self.get_object()
        serializer = self.get_serializer(price_config)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        price_config = self.get_object()
        serializer = self.get_serializer(price_config, data=request.data, partial=True)
        if serializer.is_valid():
            old_data = PricingConfigSerializer(price_config).data
            serializer.save(updated_by=self.request.user)

            action_log = ActionLog.objects.create(
                user=self.request.user,
                action_type='update',
                model_name='PricingConfig',
                record_id=price_config.pk,
                old_data=old_data,
                new_data=serializer.data
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        price_config = self.get_object()
        price_config.delete()

        action_log = ActionLog.objects.create(
            user=self.request.user,
            action_type='delete',
            model_name='PricingConfig',
            record_id=price_config.pk,
            old_data=PricingConfigSerializer(price_config).data,
            new_data={}
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class CalculatePricingView(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_dynamic_fare(self, tmf, distance, base_distance, additional_price):
        tmf_list = tmf.replace(' ', '').split(',')
        distance_list = distance.replace(' ', '').split(',')
        print(tmf_list)
        print(distance_list)

        res = 0.0
        tmf_ptr = 0
        for index in range(len(distance_list)):
            dis = float(distance_list[index])
            if index == 0:
                dis = float(distance_list[index]) - base_distance
            res += dis * float(tmf_list[tmf_ptr]) * additional_price
            if len(tmf_list) > tmf_ptr + 1:
                tmf_ptr += 1
        return res

    def post(self, request):
        data = request.data
        distance_traveled = float(data.get('distance_traveled', 0))
        distance_traveled_each_hour = data.get('distance_traveled_each_hour', '')
        waiting_time = float(data.get('waiting_time', 0))
        date = data.get('date', '')

        if not date:
            return JsonResponse({'error': 'Invalid request. Date is required.'}, status=400)

        day_of_week = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()

        active_config = get_object_or_404(PricingConfig, is_active=True, day=day_of_week)

        if distance_traveled > active_config.base_distance:
            extra_price = self.calculate_dynamic_fare(active_config.time_multiplier_factor, distance_traveled_each_hour,
                                                      float(active_config.base_distance),
                                                      float(active_config.distance_additional_price))
        else:
            extra_price = 0.0

        waiting_charges = ((waiting_time - float(active_config.waiting_time_threshold)) *
                           float(active_config.waiting_charges)) / float(active_config.waiting_time_threshold) if \
            waiting_time > float(active_config.waiting_time_threshold) else 0.0

        total_fare = float(active_config.distance_base_price) + extra_price + waiting_charges

        return JsonResponse({'Total Fare': round(total_fare, 2)})


class ActionLogListView(generics.ListAPIView):
    queryset = ActionLog.objects.all()
    serializer_class = ActionLogSerializer
    permission_classes = [IsAuthenticated]
