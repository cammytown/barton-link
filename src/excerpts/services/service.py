from threading import Thread

from ..models import Job

class Service:
    running: bool = False
    name: str

    def __init__(self, name):
        self.name = name

    def start(self):
        """
        Start service.
        """

        # If service is already running, return
        if self.running == True:
            return

        # Set running to True
        self.running = True

        # Create thread and run service
        thread = Thread(target=self.run)
        thread.start()

    def stop(self):
        """
        Stop service.
        """

        # Set running to False
        self.running = False

    def run(self):
        """
        Run service until completion or running is set to False.
        """

        raise NotImplementedError

    def get_job(self):
        """
        Get service Job database entry.
        """

        try:
            job = Job.objects.get(name=self.name)
            return job

        # If no Job exists, create one
        except Job.DoesNotExist:
            return None


    def get_status(self):
        """
        Get service status.
        """

        # Get service Job database entry
        job = self.get_job()

        return {
            "running": self.running,
            "job": job if job else None,
            "progress": job.progress if job else None,
            "subprogress": job.subprogress if job else None,
            "total": job.total if job else None,
            "percent": round(job.progress / job.total * 100, 2) if job else None,
        }
