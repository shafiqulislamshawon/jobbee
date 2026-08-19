"""
Management command: generate_job_card
Usage:
    python manage.py generate_job_card <job_id>
    python manage.py generate_job_card <job_id> --template bold
    python manage.py generate_job_card <job_id> --template luxury --no-qr
    python manage.py generate_job_card --all
    python manage.py generate_job_card --all --template editorial
"""
import os
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Generate job card image(s) for one or all jobs.'

    def add_arguments(self, parser):
        parser.add_argument(
            'job_id',
            nargs='?',
            type=int,
            help='ID of the job to generate a card for.',
        )
        parser.add_argument(
            '--template', '-t',
            default='all',
            choices=['editorial', 'bold', 'luxury', 'all'],
            help='Which template to use (default: all).',
        )
        parser.add_argument(
            '--no-qr',
            action='store_true',
            default=False,
            help='Disable QR code on the card.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Generate cards for ALL active jobs.',
        )

    def handle(self, *args, **options):
        from jobs.models import Job
        from job_card.generator import generate_job_card_from_django_job, generate_all_templates, TEMPLATE_NAMES

        show_qr = not options['no_qr']
        template = options['template']
        generate_all = options['all']

        # Determine which jobs to process
        if generate_all:
            jobs = Job.objects.filter(is_active=True)
            if not jobs.exists():
                self.stdout.write(self.style.WARNING('No active jobs found.'))
                return
            self.stdout.write(self.style.NOTICE(f'Generating cards for {jobs.count()} active jobs...'))
        elif options['job_id']:
            try:
                jobs = [Job.objects.get(pk=options['job_id'])]
            except Job.DoesNotExist:
                raise CommandError(f"Job with ID {options['job_id']} does not exist.")
        else:
            raise CommandError('Provide a job_id or use --all flag.')

        # Determine templates to render
        templates_to_run = TEMPLATE_NAMES if template == 'all' else [template]

        for job in jobs:
            self.stdout.write(f"\nJob #{job.pk}: {job.title}")
            for tmpl in templates_to_run:
                try:
                    path = generate_job_card_from_django_job(job, template=tmpl, show_qr=show_qr)
                    size_kb = os.path.getsize(path) // 1024
                    self.stdout.write(
                        self.style.SUCCESS(f"  [{tmpl.upper()}] -> {path} ({size_kb} KB)")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  [{tmpl.upper()}] ERROR: {e}")
                    )

        self.stdout.write(self.style.SUCCESS('\nDone.'))
