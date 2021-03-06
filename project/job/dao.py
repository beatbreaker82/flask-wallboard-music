from datetime import datetime
from project import db
from project.models import Job
from project import scheduler
from project.job.helpers import Alarms

# from project.job.helpers import Alarms
# import time

#
# class Alarm(object):
#     @staticmethod
#     def alarm(time_param):
#         print('{} Alarm! This alarm was scheduled at {}.'.format(time.strftime("%H:%M:%S"), time_param))


def weekday_converter(weekday):
    if weekday is True:
        return 'mon,tue,wed,thu,fri'
    else:
        return None


class JobDAO(object):
    def create_job(self, job):
        scheduled_job = scheduler.add_job(Alarms.browser_alarm, 'cron',
                                          name=job.name,
                                          hour=job.hour,
                                          minute=job.minute,
                                          second=job.second,
                                          day_of_week=weekday_converter(job.weekdays_only),
                                          args=[job.event_id])

        job.apscheduler_job_id = scheduled_job.id
        db.session.add(job)
        db.session.commit()

        # year=None, month=None, day=None, week=None, day_of_week=None, hour=None, minute=None,
        #      second=None, start_date=None, end_date=None, timezone=None
        # job = Job(name= , apscheduler_job_id=scheduled_job .id)

    def update_job(self, job):
        update_job = scheduler.get_job(job.apscheduler_job_id)

        update_job.modify(name=job.name)
        update_job.reschedule(trigger='cron',
                              hour=job.hour,
                              minute=job.minute,
                              second=job.second,
                              day_of_week=weekday_converter(job.weekdays_only))

        db.session.add(job)
        db.session.commit()

    def get_jobs(self):
        return db.session.query(Job).order_by(Job.id.asc()).all()

    def get_job_by_id(self, id_number):
        return db.session.query(Job).filter_by(id=id_number).first()

    def get_jobs_by_kwargs(self, **kwargs):
        return db.session.query(Job).filter_by(**kwargs).all()

    def delete_job(self, job):
        scheduler.remove_job(job.apscheduler_job_id)
        db.session.delete(job)
        db.session.commit()
