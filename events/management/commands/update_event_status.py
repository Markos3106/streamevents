from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event

class Command(BaseCommand):
    help = 'Updates event statuses based on scheduled date and duration.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # 1. Scheduled -> Live
        # If scheduled_date is passed and status is scheduled, make it live.
        scheduled_to_live = Event.objects.filter(status='scheduled', scheduled_date__lte=now)
        count_live = 0
        for event in scheduled_to_live:
            event.status = 'live'
            event.save()
            count_live += 1
            self.stdout.write(self.style.SUCCESS(f'Event "{event.title}" is now LIVE'))

        # 2. Live -> Finished
        # If scheduled_date + duration is passed, make it finished.
        live_events = Event.objects.filter(status='live')
        count_finished = 0
        for event in live_events:
            duration = event.get_duration()
            end_time = event.scheduled_date + duration
            if now >= end_time:
                event.status = 'finished'
                event.save()
                count_finished += 1
                self.stdout.write(self.style.SUCCESS(f'Event "{event.title}" has FINISHED'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated statuses. Live: {count_live}, Finished: {count_finished}'))
