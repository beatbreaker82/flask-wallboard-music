from flask_wtf import Form
from wtforms import StringField, IntegerField, HiddenField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Regexp

__author__ = 'mandreacchio'


class AddSongForm(Form):

    song_id = IntegerField()
    url = StringField('Youtube URL',
                      validators=[
                          DataRequired(),
                          Regexp(regex='https://www.youtube.com/.*', message=u'Invalid YouTube URL.'),
                      ])
    requester = StringField('Requester Name', validators=[DataRequired()])
    delay = IntegerField('Song delay in seconds',
                         validators=[
                             InputRequired(message=u'Must enter delay'),
                             NumberRange(min=0, max=None, message=u'Must be minimum 0')],
                         default=0)


class DeleteSongForm(Form):
    id = HiddenField()
