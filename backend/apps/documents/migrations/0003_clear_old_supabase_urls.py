# Generated manually to fix old supabase_url data

from django.db import migrations


def clear_invalid_supabase_urls(apps, schema_editor):
    """
    Clear old supabase_url fields that point to /media/ paths
    These are invalid and should use supabase_path instead
    """
    Document = apps.get_model('documents', 'Document')
    
    # Clear any supabase_url that contains "/media/"
    invalid_docs = Document.objects.filter(supabase_url__icontains='/media/')
    count = invalid_docs.update(supabase_url='')
    
    print(f"Cleared {count} invalid supabase_url fields")


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_document_supabase_path_document_supabase_url_and_more'),
    ]

    operations = [
        migrations.RunPython(clear_invalid_supabase_urls, reverse_code=migrations.RunPython.noop),
    ]
