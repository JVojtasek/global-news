import unittest
from tools.preview_radar import context,environment
from engine import build,config,countries,morning

class NewsletterSignupTest(unittest.TestCase):
    def render(self, configured):
        data=context('cs')
        data.update(briefing=morning.edition([],config.site(),'cs'),country_catalogue=countries.catalogue(),daily_quiz=None,page_type='briefing')
        data['newsletter']={'enabled':True,'briefing_api':'https://brief.example/subscribe','turnstile_site_key':'sitekey'} if configured else {'enabled':True}
        return environment().get_template('briefing.html').render(**data)
    def test_privacy_disclosure_follows_configuration(self):
        source = '## Ask us anything\ncontact'
        off = build._privacy_note(source, {'newsletter': {}}, build.STRINGS['en'])
        self.assertNotIn('Morning briefing by email', off)
        on = build._privacy_note(source, {'newsletter': {'briefing_api': 'https://brief.example/subscribe', 'turnstile_site_key':'sitekey'}}, build.STRINGS['en'])
        self.assertIn('Morning briefing by email', on)
        self.assertIn('Brevo', on)
        self.assertIn('do not collect health interests', on)

    def test_form_is_disabled_without_configuration(self):
        html=self.render(False)
        self.assertNotIn('id="briefing-email-form"',html)
        self.assertIn('Automatický odběr zatím není připojený',html)
    def test_form_uses_separate_sections_and_challenge(self):
        html=self.render(True)
        self.assertIn('id="briefing-email-form"',html)
        self.assertIn('data-action="newsletter"',html)
        self.assertIn('name="consent" required',html)
        self.assertIn('name="section" value="world"',html)
        self.assertNotIn('name="section" value="health"',html)
        self.assertNotIn('jedenkrát v sobotu',html)

    def test_weekend_navigation_is_not_an_email_section(self):
        data=context('cs')
        data.update(briefing=morning.edition([],config.site(),'cs'),country_catalogue=countries.catalogue(),daily_quiz=None,page_type='briefing')
        data['newsletter']={'enabled':True,'briefing_api':'https://brief.example/subscribe','turnstile_site_key':'sitekey'}
        data['sections']=[{'id':'world','cs':'Svět','en':'World'}, {'id':'weekend/11','cs':'Sobotní vydání','en':'Weekend'}]
        html=environment().get_template('briefing.html').render(**data)
        self.assertIn('name="section" value="world"',html)
        self.assertNotIn('name="section" value="weekend/11"',html)

if __name__ == '__main__': unittest.main()
