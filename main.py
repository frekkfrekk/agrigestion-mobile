"""
AgriGestion Mobile — Version Kivy
Application de gestion agricole pour Android.
"""
import os
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

from storage import load_data, save_data
from stats import (
    global_progress, fields_status_count, total_tasks_done, total_tasks,
    format_date,
)
from theme import get_theme, set_theme, is_dark


# ---------- Utilitaires ----------
def field_status(field):
    tasks = field.get('tasks', [])
    if tasks and all(t.get('done', False) for t in tasks):
        return "Terminé"
    return "En cours"


def field_progress(field):
    tasks = field.get('tasks', [])
    done = sum(1 for t in tasks if t.get('done', False))
    return done, len(tasks)


def notify(title, message):
    """Affiche une popup (message d'erreur / confirmation)."""
    box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    box.add_widget(Label(text=message, color=get_theme()['text']))
    btn = Button(
        text='OK', size_hint_y=None, height=dp(44),
        background_normal='', background_color=get_theme()['primary'],
        color=get_theme()['text_inverse'], bold=True,
    )
    box.add_widget(btn)
    popup = Popup(
        title=title, content=box, size_hint=(0.85, 0.4),
        background_color=get_theme()['card'],
    )
    btn.bind(on_release=popup.dismiss)
    popup.open()


def confirm(title, message, on_yes):
    """Popup de confirmation Oui/Non."""
    box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    box.add_widget(Label(text=message, color=get_theme()['text']))
    btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
    yes = Button(
        text='Oui', background_normal='',
        background_color=get_theme()['danger'], color=get_theme()['text_inverse'],
        bold=True,
    )
    no = Button(
        text='Non', background_normal='',
        background_color=get_theme()['dark'], color=get_theme()['text_inverse'],
        bold=True,
    )
    btns.add_widget(yes)
    btns.add_widget(no)
    box.add_widget(btns)
    popup = Popup(
        title=title, content=box, size_hint=(0.85, 0.4),
        background_color=get_theme()['card'],
    )

    def _yes(_):
        popup.dismiss()
        on_yes()

    yes.bind(on_release=_yes)
    no.bind(on_release=popup.dismiss)
    popup.open()


# ---------- Écrans ----------
class HomeScreen(Screen):
    progress = 0
    nb_fields = 0
    nb_en_cours = 0
    nb_termines = 0
    done_tasks = 0
    total_tasks = 0

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        data = load_data()
        fields = data.get('fields', [])
        self.progress = global_progress(fields)
        self.nb_fields = len(fields)
        en_cours, termines = fields_status_count(fields)
        self.nb_en_cours = en_cours
        self.nb_termines = termines
        self.done_tasks = total_tasks_done(fields)
        self.total_tasks = total_tasks(fields)


class FieldsScreen(Screen):
    def on_pre_enter(self):
        self.refresh_list()

    def on_search(self, text):
        self.refresh_list(text.lower().strip())

    def refresh_list(self, search_text=""):
        container = self.ids.fields_list
        container.clear_widgets()

        data = load_data()
        fields = data.get('fields', [])

        for real_idx, f in enumerate(fields):
            if search_text:
                searchable = f"{f['name']} {f['crop']} {f.get('terrain', '')}".lower()
                if search_text not in searchable:
                    continue

            done, total = field_progress(f)
            status = field_status(f)

            card = BoxLayout(
                orientation='vertical', padding=dp(10), spacing=dp(4),
                size_hint_y=None, height=dp(110),
            )
            # Fond carte
            from kivy.graphics import Color, RoundedRectangle
            with card.canvas.before:
                Color(*get_theme()['card'])
                rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])

            def _update_rect(instance, value):
                rect.pos = instance.pos
                rect.size = instance.size

            card.bind(pos=_update_rect, size=_update_rect)

            card.add_widget(Label(
                text=f"{f['name']} - {f['area']}",
                color=get_theme()['text'], bold=True, font_size='15sp',
                size_hint_y=None, height=dp(24),
            ))
            card.add_widget(Label(
                text=f"Culture: {f['crop']}  •  Terrain: {f.get('terrain', '-')}",
                color=get_theme()['text_muted'], font_size='12sp',
                size_hint_y=None, height=dp(18),
            ))
            card.add_widget(Label(
                text=f"Progression : {done}/{total} tâches accomplies",
                color=get_theme()['secondary'], font_size='12sp', bold=True,
                size_hint_y=None, height=dp(18),
            ))

            status_btn = Button(
                text=f"● {status}",
                background_normal='',
                background_color=get_theme()['primary'] if status == "En cours" else get_theme()['text_muted'],
                color=get_theme()['text_inverse'], font_size='11sp',
                size_hint_y=None, height=dp(30),
            )
            status_btn.bind(on_release=lambda _, i=real_idx: self.open_field(i))
            card.add_widget(status_btn)

            container.add_widget(card)

        if not container.children:
            container.add_widget(Label(
                text="Aucun champ trouvé" if search_text else "Aucun champ enregistré",
                color=get_theme()['text_muted'], size_hint_y=None, height=dp(60),
                halign='center',
            ))

    def open_field(self, index):
        app = App.get_running_app()
        detail = app.root.get_screen('field_detail')
        detail.field_index = index
        app.go_to('field_detail')


class FieldDetailScreen(Screen):
    field_index = 0
    field_name = ""
    field_area = ""
    field_crop = ""
    field_terrain = ""
    field_status = ""

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        data = load_data()
        if self.field_index >= len(data['fields']):
            App.get_running_app().go_to('fields')
            return
        f = data['fields'][self.field_index]
        self.field_name = f['name']
        self.field_area = f['area']
        self.field_crop = f['crop']
        self.field_terrain = f.get('terrain', '-')
        self.field_status = f"● {field_status(f)}"

        self.rebuild_tasks()

    def rebuild_tasks(self):
        container = self.ids.tasks_list
        container.clear_widgets()

        data = load_data()
        f = data['fields'][self.field_index]
        tasks = f.get('tasks', [])

        if not tasks:
            container.add_widget(Label(
                text="Aucune tâche. Ajoutez-en une ci-dessous.",
                color=get_theme()['text_muted'], size_hint_y=None, height=dp(50),
            ))
            return

        for t_idx, task in enumerate(tasks):
            row = self._make_task_row(t_idx, task)
            container.add_widget(row)

    def _make_task_row(self, t_idx, task):
        row = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(52),
            padding=dp(6), spacing=dp(6),
        )
        from kivy.graphics import Color, RoundedRectangle
        with row.canvas.before:
            Color(*get_theme()['card'])
            rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])

        def _update(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size

        row.bind(pos=_update, size=_update)

        cb = CheckBox(
            active=task.get('done', False),
            size_hint=(None, None), size=(dp(40), dp(40)),
        )
        cb.bind(active=lambda _, val, ti=t_idx: self.toggle_task(ti, val))
        row.add_widget(cb)

        lbl = Label(
            text=task['name'],
            color=get_theme()['text_muted'] if task.get('done') else get_theme()['text'],
            font_size='13sp',
        )
        row.add_widget(lbl)

        if task.get('done') and task.get('done_at'):
            date_lbl = Label(
                text=format_date(task['done_at']),
                color=get_theme()['primary'], font_size='10sp',
                size_hint=(None, None), size=(dp(110), dp(40)),
            )
            row.add_widget(date_lbl)

        edit_btn = Button(
            text='Modifier', size_hint=(None, None), size=(dp(80), dp(34)),
            background_normal='', background_color=get_theme()['secondary'],
            color=get_theme()['text_inverse'], font_size='11sp',
        )
        edit_btn.bind(on_release=lambda _, ti=t_idx: self.edit_task(ti))
        row.add_widget(edit_btn)

        del_btn = Button(
            text='Suppr.', size_hint=(None, None), size=(dp(70), dp(34)),
            background_normal='', background_color=get_theme()['danger'],
            color=get_theme()['text_inverse'], font_size='11sp',
        )
        del_btn.bind(on_release=lambda _, ti=t_idx: self.delete_task(ti))
        row.add_widget(del_btn)

        return row

    def toggle_task(self, t_idx, is_done):
        data = load_data()
        task = data['fields'][self.field_index]['tasks'][t_idx]
        task['done'] = is_done
        if is_done:
            task['done_at'] = datetime.now().isoformat()
        else:
            task.pop('done_at', None)
        save_data(data)
        self.refresh()

    def add_task(self):
        text_input = self.ids.new_task
        name = text_input.text.strip()
        if not name:
            notify("Erreur", "Veuillez saisir une tâche")
            return
        data = load_data()
        data['fields'][self.field_index].setdefault('tasks', []).append({
            'name': name, 'done': False,
        })
        save_data(data)
        text_input.text = ''
        self.rebuild_tasks()

    def edit_task(self, t_idx):
        data = load_data()
        old_name = data['fields'][self.field_index]['tasks'][t_idx]['name']

        box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        box.add_widget(Label(text="Nouveau nom :", color=get_theme()['text']))
        ti = TextInput(
            text=old_name, multiline=False,
            background_color=get_theme()['card'],
            foreground_color=get_theme()['text'],
        )
        box.add_widget(ti)
        btn = Button(
            text='Valider', size_hint_y=None, height=dp(44),
            background_normal='', background_color=get_theme()['primary'],
            color=get_theme()['text_inverse'], bold=True,
        )
        box.add_widget(btn)
        popup = Popup(
            title="Modifier la tâche", content=box, size_hint=(0.85, 0.4),
            background_color=get_theme()['card'],
        )

        def _validate(_):
            new_name = ti.text.strip()
            if new_name:
                data['fields'][self.field_index]['tasks'][t_idx]['name'] = new_name
                save_data(data)
                self.rebuild_tasks()
            popup.dismiss()

        btn.bind(on_release=_validate)
        popup.open()

    def delete_task(self, t_idx):
        def _do():
            data = load_data()
            data['fields'][self.field_index]['tasks'].pop(t_idx)
            save_data(data)
            self.rebuild_tasks()

        confirm("Confirmer", "Supprimer cette tâche ?", _do)

    def delete_field(self):
        def _do():
            data = load_data()
            data['fields'].pop(self.field_index)
            save_data(data)
            App.get_running_app().go_to('fields')

        confirm(
            "Confirmer",
            f"Supprimer le champ « {self.field_name} » ?",
            _do,
        )


class AddFieldScreen(Screen):
    edit_index = None
    edit_name = ""
    edit_area = ""
    edit_terrain = ""
    edit_crop = ""

    def on_pre_enter(self):
        if self.edit_index is None:
            self.edit_name = self.edit_area = self.edit_terrain = self.edit_crop = ""

    def save(self):
        name = self.ids.name.text.strip()
        area = self.ids.area.text.strip()
        terrain = self.ids.terrain.text.strip()
        crop = self.ids.crop.text.strip()

        if not all([name, area, terrain, crop]):
            notify("Erreur", "Veuillez remplir tous les champs")
            return

        data = load_data()
        if self.edit_index is None:
            data['fields'].append({
                'name': name, 'area': area + ' Ha',
                'terrain': terrain, 'crop': crop, 'tasks': [],
            })
        else:
            f = data['fields'][self.edit_index]
            f['name'] = name
            f['area'] = area + ' Ha'
            f['terrain'] = terrain
            f['crop'] = crop
        save_data(data)

        self.edit_index = None
        self.edit_name = self.edit_area = self.edit_terrain = self.edit_crop = ""
        App.get_running_app().go_to('fields')


class TasksScreen(Screen):
    filter_mode = 'all'

    def on_pre_enter(self):
        self.rebuild_list()

    def set_filter(self, mode):
        self.filter_mode = mode
        self.rebuild_list()

    def rebuild_list(self):
        container = self.ids.tasks_list
        container.clear_widgets()

        data = load_data()
        has_tasks = False

        for f_idx, field in enumerate(data.get('fields', [])):
            tasks_to_show = []
            for t_idx, task in enumerate(field.get('tasks', [])):
                done = task.get('done', False)
                if self.filter_mode == 'all':
                    tasks_to_show.append((t_idx, task))
                elif self.filter_mode == 'todo' and not done:
                    tasks_to_show.append((t_idx, task))
                elif self.filter_mode == 'done' and done:
                    tasks_to_show.append((t_idx, task))

            if not tasks_to_show:
                continue
            has_tasks = True

            container.add_widget(Label(
                text=f"🌾 {field['name']}",
                color=get_theme()['text'], bold=True, font_size='14sp',
                size_hint_y=None, height=dp(28), halign='left',
            ))

            for t_idx, task in tasks_to_show:
                row = self._make_task_row(f_idx, t_idx, task)
                container.add_widget(row)

        if not has_tasks:
            msg = {
                'done': "Aucune tâche terminée",
                'todo': "Aucune tâche à faire 🎉",
                'all': "Aucune tâche enregistrée.\nCréez un champ puis ajoutez-lui des tâches.",
            }[self.filter_mode]
            container.add_widget(Label(
                text=msg, color=get_theme()['text_muted'],
                size_hint_y=None, height=dp(80), halign='center',
            ))

    def _make_task_row(self, f_idx, t_idx, task):
        row = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(52),
            padding=dp(6), spacing=dp(6),
        )
        from kivy.graphics import Color, RoundedRectangle
        with row.canvas.before:
            Color(*get_theme()['card'])
            rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])

        def _update(instance, value):
            rect.pos = instance.pos
            rect.size = instance.size

        row.bind(pos=_update, size=_update)

        cb = CheckBox(
            active=task.get('done', False),
            size_hint=(None, None), size=(dp(40), dp(40)),
        )
        cb.bind(active=lambda _, val, fi=f_idx, ti=t_idx: self.toggle(fi, ti, val))
        row.add_widget(cb)

        lbl = Label(
            text=task['name'],
            color=get_theme()['text_muted'] if task.get('done') else get_theme()['text'],
            font_size='13sp',
        )
        row.add_widget(lbl)

        if task.get('done') and task.get('done_at'):
            date_lbl = Label(
                text=format_date(task['done_at']),
                color=get_theme()['primary'], font_size='10sp',
                size_hint=(None, None), size=(dp(110), dp(40)),
            )
            row.add_widget(date_lbl)

        return row

    def toggle(self, f_idx, t_idx, is_done):
        data = load_data()
        task = data['fields'][f_idx]['tasks'][t_idx]
        task['done'] = is_done
        if is_done:
            task['done_at'] = datetime.now().isoformat()
        else:
            task.pop('done_at', None)
        save_data(data)
        self.rebuild_list()


class ProfileScreen(Screen):
    dark = False
    stats_text = ""

    def on_pre_enter(self):
        self.dark = is_dark()
        data = load_data()
        total_fields = len(data['fields'])
        done = total_tasks_done(data['fields'])
        total = total_tasks(data['fields'])
        self.stats_text = f"{total_fields} Champs  •  {done}/{total} Tâches accomplies"

    def toggle_theme(self):
        set_theme("light" if is_dark() else "dark")
        App.get_running_app().apply_theme()
        self.dark = is_dark()
        self.on_pre_enter()


# ---------- Application ----------
class AgriGestionApp(App):
    def build(self):
        self.title = "AgriGestion"
        Window.softinput_mode = 'below_target'

        # Charge le fichier KV
        kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agrigestion.kv')
        Builder.load_file(kv_path)

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(FieldsScreen(name='fields'))
        sm.add_widget(FieldDetailScreen(name='field_detail'))
        sm.add_widget(AddFieldScreen(name='add_field'))
        sm.add_widget(TasksScreen(name='tasks'))
        sm.add_widget(ProfileScreen(name='profile'))
        return sm

    def go_to(self, name):
        self.root.current = name

    def apply_theme(self):
        """Force la reconstruction des écrans pour appliquer le thème."""
        for screen in self.root.screens:
            screen.property('canvas')  # noop pour rafraîchir
        self.root.current = self.root.current  # force refresh
        # Note : pour un vrai rafraîchissement, Kivy exige de recréer
        # les widgets. On force via le rechargement du KV.
        Builder.unload_file(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'agrigestion.kv'
        ))
        Builder.load_file(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'agrigestion.kv'
        ))
        # Redémarre l'écran actuel
        current = self.root.current
        self.root.current = 'home'
        self.root.current = current


if __name__ == '__main__':
    AgriGestionApp().run()
