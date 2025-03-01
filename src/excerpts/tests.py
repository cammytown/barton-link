from django.test import TestCase
from .models import Excerpt, Tag, TagType
from barton_link.parser_excerpt import ParserExcerpt
from .views.imports.utils import actualize_parser_excerpt, actualize_parser_excerpts, check_for_duplicate_excerpts

# Create your tests here.

class ExcerptImportTests(TestCase):
    def setUp(self):
        # Create a default tag type for testing
        self.tag_type = TagType.objects.create(
            name='default',
            description='Default tag type'
        )
        
        # Create a tag for testing
        self.tag = Tag.objects.create(
            name='test_tag',
            type=self.tag_type,
            description='Test tag'
        )
        
        # Create an existing excerpt for testing duplicates
        self.existing_excerpt = Excerpt.objects.create(
            content='Existing parent excerpt'
        )
        self.existing_excerpt.tags.add(self.tag)
        self.existing_excerpt.save()

    def test_duplicate_parent_with_unique_child(self):
        """
        Test that when a parent excerpt is a duplicate but its child is unique,
        the child is still saved and linked to the existing parent.
        """
        # Create a parent excerpt that matches an existing one
        parent = ParserExcerpt(
            content='Existing parent excerpt',
            tags=['test_tag']
        )
        
        # Add a unique child to the parent
        child = ParserExcerpt(
            content='Unique child excerpt',
            tags=['test_tag']
        )
        parent.children.append(child)
        
        # Process the parent excerpt
        parent_instance, created = actualize_parser_excerpt(parent)
        
        # Verify that the parent is not created (it's a duplicate)
        self.assertFalse(created)
        self.assertEqual(parent_instance.id, self.existing_excerpt.id)
        
        # Verify that the child was added to the existing parent
        self.assertEqual(parent_instance.children.count(), 1)
        self.assertEqual(parent_instance.children.first().content, 'Unique child excerpt')
        
        # Verify that the child exists in the database
        self.assertTrue(Excerpt.objects.filter(content='Unique child excerpt').exists())

    def test_actualize_parser_excerpts_with_duplicates(self):
        """
        Test that actualize_parser_excerpts correctly handles a list of excerpts
        where some are duplicates with unique children.
        """
        # Create a list with a duplicate parent and a unique excerpt
        parent = ParserExcerpt(
            content='Existing parent excerpt',
            tags=['test_tag']
        )
        
        # Add a unique child to the parent
        child = ParserExcerpt(
            content='Unique child excerpt',
            tags=['test_tag']
        )
        parent.children.append(child)
        
        # Create another unique excerpt
        unique = ParserExcerpt(
            content='Another unique excerpt',
            tags=['test_tag']
        )
        
        # Process the list of excerpts
        created, duplicates = actualize_parser_excerpts([parent, unique])
        
        # Verify that only the unique excerpt was created
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].content, 'Another unique excerpt')
        
        # Verify that the duplicate parent is in the duplicates list
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0].content, 'Existing parent excerpt')
        
        # Verify that the child was added to the existing parent
        parent_in_db = Excerpt.objects.get(content='Existing parent excerpt')
        self.assertEqual(parent_in_db.children.count(), 1)
        self.assertEqual(parent_in_db.children.first().content, 'Unique child excerpt')

    def test_multiple_duplicate_parents_with_different_children(self):
        """
        Test that when multiple instances of the same parent with different children
        are processed, all unique children are saved and linked to the existing parent.
        """
        # Create first parent excerpt that matches an existing one
        parent1 = ParserExcerpt(
            content='Existing parent excerpt',
            tags=['test_tag']
        )
        
        # Add first unique child to the parent
        child1 = ParserExcerpt(
            content='Unique child one',
            tags=['test_tag']
        )
        parent1.children.append(child1)
        
        # Create second parent excerpt that matches the same existing one
        parent2 = ParserExcerpt(
            content='Existing parent excerpt',
            tags=['test_tag']
        )
        
        # Add second unique child to the parent
        child2 = ParserExcerpt(
            content='Unique child two',
            tags=['test_tag']
        )
        parent2.children.append(child2)
        
        # Process both parent excerpts
        non_duplicates, duplicates = check_for_duplicate_excerpts([parent1, parent2])
        
        # Verify that both parents are in non_duplicates because they have children
        self.assertEqual(len(non_duplicates), 2)
        
        # Process the non-duplicates
        created_excerpts, duplicate_excerpts = actualize_parser_excerpts(non_duplicates)
        
        # Verify that the parent exists in the database
        parent_in_db = Excerpt.objects.get(content='Existing parent excerpt')
        
        # Verify that both children were added to the existing parent
        self.assertEqual(parent_in_db.children.count(), 2)
        
        # Get the content of all children
        child_contents = set(parent_in_db.children.values_list('content', flat=True))
        
        # Verify that both unique children are in the set
        self.assertIn('Unique child one', child_contents)
        self.assertIn('Unique child two', child_contents)
