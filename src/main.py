import argparse
import time
import logging
import shutil
import os
import hashlib

class SyncHandler:
    def __init__(self, source_folder, replica_folder):
        self.source_folder = source_folder
        self.replica_folder = replica_folder

    def sync(self):
        self._sync_folder_content()
        self._remove_files_not_in_source()

    def _sync_folder_content(self):
        # walking through folders recursively
        for root, dirs, files in os.walk(self.source_folder):
            for dir_ in dirs:
                src_dir = os.path.join(root, dir_)
                dest_dir = os.path.join(self.replica_folder, os.path.relpath(src_dir, self.source_folder))
                if not os.path.exists(dest_dir):
                    logging.info(f"Folder created in source folder: {src_dir}")
                self._create_directory(os.path.join(root, dir_))

            for file_ in files:
                source_file_path = os.path.join(root, file_)
                replica_file_path = os.path.join(self.replica_folder, os.path.relpath(source_file_path, self.source_folder))
                
                source_hash = self._hash_file(source_file_path)
                replica_hash = self._hash_file(replica_file_path) if os.path.exists(replica_file_path) else None

                # comparing hashes
                if replica_hash != source_hash:
                    if not os.path.exists(replica_file_path):
                        logging.info(f"File in source folder created: {file_}")
                        logging.info(f"File {source_file_path} synchronized to {replica_file_path}")
                    else:
                        logging.info(f"File in source folder modified: {file_}")
                        logging.info(f"File content in {source_file_path} synchronized to {replica_file_path}")
                    shutil.copy2(source_file_path, replica_file_path)

    def _create_directory(self, src_dir):
        dest_dir = os.path.join(self.replica_folder, os.path.relpath(src_dir, self.source_folder))
        
        # check if the directory already exists in the replica folder
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)  # ensure subdirectories exist
            logging.info(f"Folder in source directory: {src_dir} copied to: {dest_dir}")
    
    # hash function, using MD5
    def _hash_file(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _remove_files_not_in_source(self):
        for root, dirs, files in os.walk(self.replica_folder):
            for file_ in files:
                src_file = os.path.join(root, file_)
                dest_file = os.path.join(self.source_folder, os.path.relpath(src_file, self.replica_folder))
                if not os.path.exists(dest_file):
                    os.remove(src_file)
                    logging.info(f"File deletion from source directory synchronized in replica folder: {src_file}")

            for dir_ in dirs:
                src_dir = os.path.join(root, dir_)
                dest_dir = os.path.join(self.source_folder, os.path.relpath(src_dir, self.replica_folder))
                if not os.path.exists(dest_dir):
                    shutil.rmtree(src_dir)
                    logging.info(f"Directory deletion from source directory synchronized in replica folder: {src_dir}")

def main():
    parser = argparse.ArgumentParser(description='Synchronizing folders')
    parser.add_argument('source_folder', type=str, help='Path to source folder')
    parser.add_argument('replica_folder', type=str, help='Path to replica folder')
    parser.add_argument('-i', '--interval', type=int, default=1, help='Sync interval in seconds (default: 1)')
    parser.add_argument('-l', '--log_file', type=str, default='sync_log.txt', help='Path to log file (default: sync_log.txt)')
    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(args.log_file),
            logging.StreamHandler()
        ]
    )

    sync_handler = SyncHandler(args.source_folder, args.replica_folder)
    logging.info("Folder synchronization starts...")
    try:
        while True:
            sync_handler.sync()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("Synchronization ended by user...")

if __name__ == "__main__":
    main()