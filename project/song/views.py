#################
#### imports ####
#################
import os
import random
from flask import render_template, Blueprint, url_for, redirect, flash, request
from project.models import SongRequest, SongFile
from project.song.forms import AddSongForm, DeleteSongForm
from project.song.helpers import Downloader
from project.song.dao import SongRequestDAO, SongFileDAO
from project.event.dao import EventDAO

################
#### config ####
################

song_blueprint = Blueprint('song', __name__,)
song_request_dao = SongRequestDAO()
song_file_dao = SongFileDAO()
event_dao = EventDAO()

################
#### routes ####
################


@song_blueprint.route('/songs/add/<int:event_id>', methods=['GET', 'POST'])
def add(event_id):
    form = AddSongForm(request.form)
    d = Downloader()
    if form.validate_on_submit():

        youtube_info = d.check_youtube(form.url.data)

        # If the video exists on youtube then save the details to DB
        if youtube_info:

            song_from_db = song_file_dao.get_song_file_by_youtube_id(youtube_info['id'])
            # If it's not already in the db, then create it
            if song_from_db is None:
                song_file = SongFile(
                    url=form.url.data,
                    title=youtube_info['title'],
                    youtube_id=youtube_info['id']
                )
                song_file_dao.create_song_file(song_file)
                song_from_db = song_file

            # attempt a download
            d.download(youtube_info['id'])

            # do this last - with the file ID
            song_request = SongRequest(
                requester=form.requester.data,
                delay=form.delay.data,
                song_file_id=song_from_db.id,
                event_id=event_id
            )
            song_request_dao.create_song_request(song_request)
            flash('Thank you for adding a song. Attempting background download.', 'success')
            return redirect(url_for("song.view", event_id=event_id))
        else:
            flash('There was an error finding the YouTube video, please try another URL.', 'danger')

    return render_template('songs/add.html', form=form)


@song_blueprint.route('/songs/view/<int:event_id>')
def view(event_id):
    form = DeleteSongForm()
    requests = song_request_dao.get_song_requests_by_kwargs(event_id=event_id)
    return render_template('songs/view.html', requests=requests, event_id=event_id, form=form)


@song_blueprint.route('/songs/delete', methods=['POST'])
def delete():
    form = DeleteSongForm()
    song_object = song_request_dao.get_song_request_by_id(form.id.data)

    if song_object is not None:
        song_request_dao.delete_song_request(song_object)
        # TODO: Cleanup of song_files and physical files
        # try:
        #     os.remove(os.path.join(app.config['VIDEOS_FOLDER'], song_object.file))
        # except OSError as e:
        #     print("Error removing file", e)
        flash('The song was deleted. Why not add a new one?', 'success')
    else:
        flash('Song id not found, it may have already been deleted', 'danger')
    return redirect(url_for('song.view', event_id=song_object.event_id))


@song_blueprint.route('/songs/redownload/<int:request_id>')
def redownload(request_id):
    song_request = song_request_dao.get_song_request_by_id(request_id)
    song_request.song.percent_complete = "0%"
    song_request.song.completed = False
    song_request_dao.update_song_request(song_request)
    d = Downloader()
    d.download(song_request.song.youtube_id)
    flash('Attempting background download again', 'success')
    return redirect(url_for('song.view', event_id=song_request.event_id))


@song_blueprint.route('/songs/playsong/<int:request_id>')
def play(request_id):
    song_request = song_request_dao.get_song_request_by_id(request_id)
    event = event_dao.get_event_by_id(song_request.event_id)
    return render_template('songs/playsong.html', request=song_request, event=event)


@song_blueprint.route('/songs/playrandom/<int:event_id>')
def playrandom(event_id):
    song_requests = song_request_dao.get_song_requests_by_kwargs(event_id=event_id)
    rand_request = random.choice(song_requests)
    event = event_dao.get_event_by_id(event_id)
    return render_template('songs/playsong.html', request=rand_request, event=event)
