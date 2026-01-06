"""
Background Jobs Service
Handles async LLM generation and heavy computations in background
"""
import asyncio
from typing import Callable, Any, Optional
from enum import Enum
from datetime import datetime


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BackgroundJob:
    """Single background job"""
    def __init__(self, job_id: str, task_name: str, coro):
        self.job_id = job_id
        self.task_name = task_name
        self.coro = coro
        self.status = JobStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.task = None
    
    def get_info(self) -> dict:
        """Get job information"""
        duration = None
        if self.completed_at and self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
        
        return {
            "job_id": self.job_id,
            "task_name": self.task_name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": duration
        }


class BackgroundJobQueue:
    """Simple background job queue for async tasks"""
    
    _jobs: dict[str, BackgroundJob] = {}
    _task_counter = 0
    
    @classmethod
    async def submit(cls, coro, task_name: str = "task") -> str:
        """
        Submit a coroutine to run in background
        Returns job_id for tracking
        """
        job_id = f"{task_name}_{cls._task_counter}_{int(datetime.now().timestamp() * 1000)}"
        cls._task_counter += 1
        
        job = BackgroundJob(job_id, task_name, coro)
        cls._jobs[job_id] = job
        
        # Create and schedule task
        job.task = asyncio.create_task(cls._run_job(job))
        
        print(f"📋 Job submitted: {job_id}")
        return job_id
    
    @classmethod
    async def _run_job(cls, job: BackgroundJob) -> None:
        """Run a single job and handle result/error"""
        try:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            
            job.result = await job.coro
            job.status = JobStatus.COMPLETED
            
            print(f"✅ Job completed: {job.job_id}")
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            print(f"❌ Job failed: {job.job_id} - {str(e)}")
        finally:
            job.completed_at = datetime.now()
    
    @classmethod
    def get_job(cls, job_id: str) -> Optional[BackgroundJob]:
        """Get job by ID"""
        return cls._jobs.get(job_id)
    
    @classmethod
    def get_job_info(cls, job_id: str) -> Optional[dict]:
        """Get job information"""
        job = cls.get_job(job_id)
        return job.get_info() if job else None
    
    @classmethod
    async def get_result(cls, job_id: str, timeout: int = 30) -> Any:
        """
        Wait for job result with timeout
        Useful for polling
        """
        job = cls.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status == JobStatus.COMPLETED:
            return job.result
        elif job.status == JobStatus.FAILED:
            raise Exception(f"Job failed: {job.error}")
        
        # Wait with timeout
        try:
            await asyncio.wait_for(job.task, timeout=timeout)
            if job.status == JobStatus.COMPLETED:
                return job.result
            elif job.status == JobStatus.FAILED:
                raise Exception(f"Job failed: {job.error}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
    
    @classmethod
    async def list_jobs(cls, status: Optional[JobStatus] = None) -> list[dict]:
        """List all jobs, optionally filtered by status"""
        jobs = cls._jobs.values()
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return [job.get_info() for job in jobs]
    
    @classmethod
    async def cleanup_completed(cls, keep_count: int = 50) -> int:
        """Remove old completed jobs, keeping only recent ones"""
        completed = [
            (job_id, job) for job_id, job in cls._jobs.items()
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED)
        ]
        
        # Sort by completion time, descending
        completed.sort(key=lambda x: x[1].completed_at or datetime.now(), reverse=True)
        
        # Keep only the most recent
        to_remove = completed[keep_count:]
        removed_count = 0
        
        for job_id, _ in to_remove:
            del cls._jobs[job_id]
            removed_count += 1
        
        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} old jobs")
        
        return removed_count
