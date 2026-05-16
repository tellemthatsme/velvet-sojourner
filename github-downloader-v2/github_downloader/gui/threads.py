from PyQt6.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    """Thread for downloading repositories with progress"""
    
    progress_updated = pyqtSignal(object)
    download_complete = pyqtSignal(str, bool)
    
    def __init__(self, downloader, task_id, parent=None):
        super().__init__(parent)
        self.downloader = downloader
        self.task_id = task_id

    def run(self):
        def progress_callback(task):
            self.progress_updated.emit(task)
            
        # Set callback
        self.downloader.progress_callback = progress_callback
        
        success = self.downloader.start_download(self.task_id)
        self.download_complete.emit(self.task_id, success)
