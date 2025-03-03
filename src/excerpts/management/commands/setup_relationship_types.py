from django.core.management.base import BaseCommand
from excerpts.utils import setup_default_relationship_types

class Command(BaseCommand):
    help = 'Sets up default relationship types for the application'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update of existing relationship types to match defaults',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        created_count, updated_count = setup_default_relationship_types(force=force)
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} relationship types')
            )
        
        if updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} relationship types')
            )
            
        if created_count == 0 and updated_count == 0:
            self.stdout.write('All default relationship types already exist') 