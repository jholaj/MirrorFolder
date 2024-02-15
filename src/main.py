import argparse
import time
import logging
import shutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# define event handler for folder changes
class SyncHandler(FileSystemEventHandler):
    def __init__(self, source_folder, replica_folder):
        self.source_folder = source_folder
        self.replica_folder = replica_folder

    def on_created(self, event):
        if event.is_directory:      # for folders
            logging.info(f"Directory created: {event.src_path}")
            self.sync_folder(event.src_path)
        else:
            logging.info(f"File created: {event.src_path}")
            self.sync_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"File modified: {event.src_path}")
            self.sync_file(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            self.sync_folder(event.src_path)
            logging.info(f"Directory deleted: {event.src_path}")
        else:
            self.sync_delete(event.src_path)
            logging.info(f"File deleted: {event.src_path}")
    
    def sync_delete(self, src_path):
        relative_path = os.path.relpath(src_path, self.source_folder)
        dest_path = os.path.join(self.replica_folder, relative_path)

        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):        
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)    # deleting in replica folder
        else:
            logging.warning(f"File or folder to delete not found: {dest_path}")

    def sync_file(self, src_path):
        relative_path = os.path.relpath(src_path, self.source_folder)
        dest_path = os.path.join(self.replica_folder, relative_path)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dest_path)
    
    def sync_folder(self, src_path):
        relative_path = os.path.relpath(src_path, self.source_folder)
        dest_path = os.path.join(self.replica_folder, relative_path)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        os.makedirs(dest_path, exist_ok=True)  # ensure the directory exists in the replica folder
        for root, dirs, files in os.walk(src_path):
            for dir_ in dirs:
                src_dir = os.path.join(root, dir_)
                dest_dir = os.path.join(self.replica_folder, os.path.relpath(src_dir, self.source_folder))
                os.makedirs(dest_dir, exist_ok=True)  # ensure subdirectories exist

def main():
    parser = argparse.ArgumentParser(description='Synchronizing folders')
    parser.add_argument('source_folder', type=str, help='Path to source folder')
    parser.add_argument('replica_folder', type=str, help='Path to replica folder')
    parser.add_argument('-i', '--interval', type=int, default=10, help='Sync interval in seconds (default: 10)')
    parser.add_argument('-l', '--log_file', type=str, default='sync_log.txt', help='Path to log file (default: sync_log.txt)')
    args = parser.parse_args()

    # logger
    # needs initializing logging.root.handlers or file will be empty
    logging.root.handlers = []
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(args.log_file),
            logging.StreamHandler()
        ]
    )

    # start synchronization
    event_handler = SyncHandler(args.source_folder, args.replica_folder)
    observer = Observer()
    observer.schedule(event_handler, args.source_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(args.interval)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
