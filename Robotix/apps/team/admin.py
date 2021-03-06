from django.http import HttpResponse
from django.contrib import admin
from django import forms

from import_export.admin import ExportMixin
from import_export import resources
from django_object_actions import DjangoObjectActions

from miscellaneous.models import College

from .models import *


def TeamInlineFactory(event):
    class TeamInline(admin.StackedInline):
        model = event.participant.through
        extra = 0

    return TeamInline


class ParticipantCollegeFilter(admin.SimpleListFilter):
    title = 'College'
    parameter_name = 'college'

    def lookups(self, request, model_admin):
        return College.objects.values_list('pk', 'name')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(participant__college=self.value()).distinct()
        return queryset


def TeamFormFactory(event):
    class TeamForm(forms.ModelForm):

        class Meta:
            model = event
            fields = '__all__'

        def clean_participant(self):
            if self.cleaned_data['participant'].count() > self.Meta.model.max_team_size:
                raise forms.ValidationError(
                    'Max team size is '+str(self.Meta.model.max_team_size),
                    code='invalid'
                )
            return self.cleaned_data['participant']

    return TeamForm

class TeamResource(resources.ModelResource):

    class Meta:
        model = Fortress
        use_transactions = True

    def dehydrate_participant(self, team):
        import os
        return os.linesep.join(
            '{} ({})'.format(participant.name, participant.mobile) \
            for participant in team.participant.all()
        )

    def dehydrate_state(self, team):
        return team.state.name

    def dehydrate_country(self, team):
        return team.country.name


class TeamAdmin(ExportMixin, DjangoObjectActions, admin.ModelAdmin):
    resource_class = TeamResource
    search_fields = [
        '=participant__first_name',
        '=participant__last_name',
        'participant__email',
        'participant__mobile',
    ]
    actions = [
        'verify',
        'qualify_to_round_two',
        'qualify_to_round_three',
    ]
    objectactions = [
        'verify_this',
        'qualify_this',
        'print_participation',
        'print_appreciation',
    ]

    def get_fieldsets(self, request, obj=None, **kwargs):
        fieldsets = [
            (None, {
                'fields': ('participant',),
                'classes': ('wide',)
            }),
            ('Complete Postal Address', {
                'fields': (
                    ('name',),
                    ('street', 'locality'),
                    ('city', 'pin'),
                    ('state', 'country'),
                ),
                'classes': ('wide'),
                'description': 'Enter the complete address. We may have to post certificates to this address.',
            }),
            ('Scoring', {
                'fields': (
                    ('round_one',),
                    ('round_two', 'qualify_round_one',),
                    ('round_three', 'qualify_round_two',),
                ),
                'classes': ('wide'),
            }),
            ('Help Desk', {
                'fields': (
                    ('verification', 'certificate',),
                ),
                'classes': ('wide'),
            }),
        ]
        if not request.user.is_superuser:
            return fieldsets[:-2]
        return fieldsets

    def get_list_display(self, request, obj=None, **kwargs):
        list_display = [
            'round_one',
            'qualify_round_one',
            'round_two',
            'qualify_round_two',
            'round_three',
        ]
        if request.user.get_username() == 'helpdesk':
            return ['__str__', 'verification', 'certificate',] + list_display
        return ['__str__',] + list_display

    def get_list_filter(self, request, obj=None, **kwargs):
        list_filter = [
            ParticipantCollegeFilter,
            'qualify_round_one',
            'qualify_round_two',
        ]
        if request.user.get_username() == 'helpdesk':
            return ['verification', 'certificate',] + list_filter
        return list_filter

    def verify(self, request, queryset):
        rows = queryset.update(verification=True)
        self.message_user(request,  '{} teams marked as verified'.format(rows))
    verify.short_description = 'Verify selected teams'

    def qualify_to_round_two(self, request, queryset):
        rows = queryset.update(qualify_round_one=True)
        self.message_user(request, '{} teams are qualified to Round Two')
    qualify_to_round_two.short_description = 'Qualify these teams to Round Two'

    def qualify_to_round_three(self, request, queryset):
        rows = queryset.update(qualify_round_two=True)
        self.message_user(request, '{} teams are qualified to Round Three')
    qualify_to_round_three.short_description = 'Qualify these teams to Round Three'

    def print_participation(self, request, team):
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Certificate-{}.pdf"'.format(team)
        p = canvas.Canvas(response)
        for participant in team.participant.all():
            text_obj = p.beginText()
            text_obj.setFont('Helvetica-Oblique', 16)
            text_obj.setTextOrigin(3.7*inch, 5.38*inch)
            text_obj.textLine(participant.name.title())
            text_obj.setTextOrigin(1.5*inch, 4.94*inch)
            if len(participant.college.name) > 60:
                text_obj.setHorizScale(80)
            text_obj.textLine(participant.college.name)
            text_obj.setTextOrigin(3*inch, 4.54*inch)
            text_obj.textLine(self.form.Meta.model._meta.verbose_name)
            p.drawText(text_obj)
            p.showPage()
        p.save()
        return response
    print_participation.label = 'Print Participation Certificates'


    def print_appreciation(self, request, team):
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Certificate-{}.pdf"'.format(team)
        p = canvas.Canvas(response)
        for participant in team.participant.all():
            text_obj = p.beginText()
            text_obj.setFont('Helvetica-Oblique', 16)
            text_obj.setTextOrigin(3.5*inch, 5*inch)
            text_obj.textLine(participant.name.title())
            text_obj.setTextOrigin(1.5*inch, 4.5*inch)
            if len(participant.college.name) > 60:
                text_obj.setHorizScale(80)
            text_obj.textLine(participant.college.name)
            text_obj.setTextOrigin(4*inch, 4.5*inch)
            text_obj.textLine(self.form.Meta.model._meta.verbose_name)
            p.drawText(text_obj)
            p.showPage()
        p.save()
        return response
    print_appreciation.label = 'Print Appreciation Certificates'

    def verify_this(self, request, team):
        team.verification=True
        team.save()
        self.message_user(request, 'Team {} is marked as verified'.format(team))
    verify_this.label = 'Verify'

    def qualify_this(self, request, team):
        if team.qualify_round_one:
            team.qualify_round_two = True
        else:
            team.qualify_round_one = True
        team.save()
    qualify_this.label = 'Qualify to the next Round'


@admin.register(PolesApart)
class PolesApartAdmin(TeamAdmin):
    form = TeamFormFactory(PolesApart)
    inlines = [
        TeamInlineFactory(PolesApart),
    ]


@admin.register(Fortress)
class FortressAdmin(TeamAdmin):
    form = TeamFormFactory(Fortress)
    inlines = [
        TeamInlineFactory(Fortress),
    ]


@admin.register(Stax)
class StaxAdmin(TeamAdmin):
    form = TeamFormFactory(Stax)
    inlines = [
        TeamInlineFactory(Stax),
    ]
