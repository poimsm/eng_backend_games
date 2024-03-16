# Framework
from django.core.management.base import BaseCommand
from django.conf import settings
import traceback

# Custom
from api.models import Question
from api.helpers import console, read_JSON_file


class Command(BaseCommand):
    help = 'Create questions'

    def handle(self, *args, **kwargs):

        console.info('--------------------------------')
        console.info('    POPULATE QUESTIONS          ')
        console.info('--------------------------------')

        try:
            console.info('Reading questions JSON files...')
            normal_questions = read_JSON_file('data/questions/normal.json')
            intrig_questions = read_JSON_file('data/questions/intriguing.json')
            fantasy_questions = read_JSON_file('data/questions/fantasy.json')
            # outdoor_questions = read_JSON_file('data/questions/outdoor.json')
            job_questions = read_JSON_file('data/questions/jobs.json')
            # picture_questions = read_JSON_file('data/questions/picture.json')
            # puzzle_questions = read_JSON_file('data/questions/puzzle.json')
            # rpg_questions = read_JSON_file('data/questions/rpg.json')

            console.info('[x] Normal: ' + str(len(normal_questions)))
            console.info('[x] Intriguing: ' + str(len(intrig_questions)))
            console.info('[x] Fantasy: ' + str(len(fantasy_questions)))
            # console.info('[x] Outdoor: ' + str(len(outdoor_questions)))
            console.info('[x] Jobs: ' + str(len(job_questions)))
            # console.info('[x] Picture: ' + str(len(picture_questions)))
            # console.info('[x] Puzzle: ' + str(len(puzzle_questions)))
            # console.info('[x] RPG: ' + str(len(rpg_questions)))

            console.info('Creating questions...')
            self.create_questions(normal_questions)
            self.create_questions(intrig_questions)
            self.create_questions(fantasy_questions)
            # self.create_questions(outdoor_questions)
            self.create_questions(job_questions)
            # self.create_questions(picture_questions)
            # self.create_questions(puzzle_questions)
            # self.create_questions(rpg_questions)

            console.info('Done')
        except:
            traceback.print_exc()
            console.error('Process Failed!')

    def create_questions(self, questions):
        for q in questions:

            if not q['ready']:
                continue
            example = read_JSON_file(q['example'])

            if example:
                example['voice_url'] = self.create_url(example['voice_url'])

            # scenario = {} if q['type'] == 3 else None
            scenario = q.get('scenario', None)

            if scenario:
                for i, part in enumerate(scenario['parts']):
                    part_options = part.get('options', None)
                    part_voice = part.get('voice_url', None)
                    part_image = part.get('image_url', None)

                    if part_image:
                        scenario['parts'][i]['image_url'] = self.create_url(
                            part_image)

                    if part_voice:
                        scenario['parts'][i]['voice_url'] = self.create_url(
                            part_voice)

                    if part_options:
                        for j, opt in enumerate(part_options):
                            opt_img = opt['image_url']
                            if opt_img:
                                scenario['parts'][i]['options'][j]['image_url'] = self.create_img_url(
                                    opt_img)

            voice_url = self.create_url(q['voice_url'])
            image_url = self.create_url(q['image_url'])
            style = self.create_style(q.get('style', None))
            difficulty = self.difficulty_level(q['difficulty'])

            translations = read_JSON_file(q['translations'])
            if not translations:
                print(f"MISSING translations: {q['question']}")

            Question(
                question=q['question'],
                translations=translations,
                voice_url=voice_url,
                image_url=image_url,
                difficulty=difficulty,
                category=q['category'],
                notes=q.get('help', None),
                type=q['type'],
                code=q.get('code', None),
                ranking=q.get('ranking', None),
                example=example,
                scenario=scenario,
                style=style,
                status=0 if q['disabled'] else 1
            ).save()

    def create_url(self, chunk):
        media = settings.SITE_DOMAIN + '/media'
        return None if not chunk else f"{media}/{chunk}"

    def difficulty_level(self, difficulty):
        level = {
            'easy': 0,
            'moderate': 1,
            'complex': 2,
        }
        return level[difficulty]

    def create_style(self, style):
        if not style:
            return {
                'background_screen': '#171717',
                'background_challenge': '#2A262C',
                'question_opacity': 0.3,
            }

        return {
            'background_screen': style.get('background_screen', '#171717'),
            'background_challenge': style.get('background_challenge', '#2A262C'),
            'question_opacity': style.get('question_opacity', 0.3),
        }
