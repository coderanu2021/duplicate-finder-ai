import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from duplicate_detector import DuplicateDetector
import threading
import queue
import shutil
import mimetypes

class DuplicateFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Document Finder")
        self.root.geometry("800x600")
        
        # Initialize the duplicate detector
        self.detector = DuplicateDetector()
        
        # Create message queue for thread communication
        self.queue = queue.Queue()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Directory selection
        ttk.Label(self.main_frame, text="Select Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dir_path = tk.StringVar()
        self.dir_entry = ttk.Entry(self.main_frame, textvariable=self.dir_path, width=50)
        self.dir_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_directory).grid(row=0, column=2, padx=5)
        
        # Similarity threshold
        ttk.Label(self.main_frame, text="Similarity Threshold:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.threshold = tk.DoubleVar(value=0.95)
        self.threshold_scale = ttk.Scale(self.main_frame, from_=0.5, to=1.0, 
                                       variable=self.threshold, orient=tk.HORIZONTAL)
        self.threshold_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.threshold_label = ttk.Label(self.main_frame, text="0.95")
        self.threshold_label.grid(row=1, column=2, padx=5)
        self.threshold_scale.configure(command=self.update_threshold_label)
        
        # Search button
        self.search_button = ttk.Button(self.main_frame, text="Find Duplicates", 
                                      command=self.start_search)
        self.search_button.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress", padding="5")
        self.progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Results treeview
        self.create_results_tree()
        
        # Action buttons frame
        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Delete selected button
        self.delete_button = ttk.Button(self.action_frame, text="Delete Selected", 
                                      command=self.delete_selected, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Move to trash button
        self.trash_button = ttk.Button(self.action_frame, text="Move to Trash", 
                                     command=self.move_to_trash, state='disabled')
        self.trash_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Start checking the queue
        self.check_queue()
        
    def create_results_tree(self):
        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=('File 1', 'File 2', 'Similarity', 'Path 1', 'Path 2'), 
                                show='headings', height=10)
        self.tree.heading('File 1', text='File 1')
        self.tree.heading('File 2', text='File 2')
        self.tree.heading('Similarity', text='Similarity')
        
        # Configure column widths
        self.tree.column('File 1', width=300)
        self.tree.column('File 2', width=300)
        self.tree.column('Similarity', width=100)
        self.tree.column('Path 1', width=0, stretch=False)  # Hidden column
        self.tree.column('Path 2', width=0, stretch=False)  # Hidden column
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Add right-click menu
        self.create_context_menu()
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open File 1", command=lambda: self.open_file(0))
        self.context_menu.add_command(label="Open File 2", command=lambda: self.open_file(1))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Selected", command=self.delete_selected)
        self.context_menu.add_command(label="Move to Trash", command=self.move_to_trash)
        
        # Bind right-click event
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        # Select the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def open_file(self, file_index):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        values = self.tree.item(item)['values']
        file_path = values[3 + file_index]  # Path 1 or Path 2
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # Unix-like
                import subprocess
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            
    def on_select(self, event):
        # Enable/disable delete buttons based on selection
        if self.tree.selection():
            self.delete_button.configure(state='normal')
            self.trash_button.configure(state='normal')
        else:
            self.delete_button.configure(state='disabled')
            self.trash_button.configure(state='disabled')
        
    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        if messagebox.askyesno("Confirm Delete", 
                             "Are you sure you want to permanently delete the selected files?"):
            for item in selected_items:
                values = self.tree.item(item)['values']
                file1_path = values[3]  # Path 1
                file2_path = values[4]  # Path 2
                
                try:
                    # Delete both files
                    os.remove(file1_path)
                    os.remove(file2_path)
                    # Remove from treeview
                    self.tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete files: {str(e)}")
            
            self.status_var.set("Selected files deleted")
            
    def move_to_trash(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        if messagebox.askyesno("Confirm Move to Trash", 
                             "Are you sure you want to move the selected files to trash?"):
            for item in selected_items:
                values = self.tree.item(item)['values']
                file1_path = values[3]  # Path 1
                file2_path = values[4]  # Path 2
                
                try:
                    # Move both files to trash
                    self.move_to_trash_file(file1_path)
                    self.move_to_trash_file(file2_path)
                    # Remove from treeview
                    self.tree.delete(item)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to move files to trash: {str(e)}")
            
            self.status_var.set("Selected files moved to trash")
            
    def move_to_trash_file(self, file_path):
        try:
            # Use send2trash if available, otherwise use system trash
            try:
                from send2trash import send2trash
                send2trash(file_path)
            except ImportError:
                # Fallback to system trash
                if os.name == 'nt':  # Windows
                    try:
                        import win32com.client
                        shell = win32com.client.Dispatch("Shell.Application")
                        shell.Namespace(10).ParseName(file_path).InvokeVerb("delete")
                    except ImportError:
                        # If win32com is not available, use direct deletion
                        os.remove(file_path)
                else:  # Unix-like
                    import subprocess
                    subprocess.run(['gvfs-trash', file_path])
        except Exception as e:
            raise Exception(f"Failed to move {file_path} to trash: {str(e)}")
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_path.set(directory)
            
    def update_threshold_label(self, value):
        self.threshold_label.configure(text=f"{float(value):.2f}")
        
    def start_search(self):
        directory = self.dir_path.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory")
            return
            
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Disable search button and show progress
        self.search_button.configure(state='disabled')
        self.progress['value'] = 0
        self.progress_label.configure(text="Initializing...")
        self.status_var.set("Searching for duplicates...")
        
        # Start search in a separate thread
        thread = threading.Thread(target=self.search_duplicates)
        thread.daemon = True
        thread.start()
        
    def search_duplicates(self):
        try:
            directory = self.dir_path.get()
            threshold = self.threshold.get()
            
            # Get all files in the directory
            file_paths = []
            # Common document extensions
            extensions = [
                '.txt', '.doc', '.docx', '.pdf', '.rtf',  # Text documents
                '.jpg', '.jpeg', '.png', '.gif', '.bmp',  # Images
                '.mp3', '.wav', '.flac', '.m4a',          # Audio
                '.mp4', '.avi', '.mkv', '.mov',           # Video
                '.xls', '.xlsx', '.csv',                  # Spreadsheets
                '.ppt', '.pptx',                          # Presentations
                '.zip', '.rar', '.7z',                    # Archives
                '.py', '.java', '.cpp', '.js', '.html', '.css'  # Code files
            ]
            
            for ext in extensions:
                file_paths.extend([str(f) for f in Path(directory).rglob(f"*{ext}")])
            
            if not file_paths:
                self.queue.put(("error", "No files found in the selected directory"))
                return
                
            total_files = len(file_paths)
            self.queue.put(("progress_max", total_files))
            
            # Process files in batches
            batch_size = 10
            for i in range(0, total_files, batch_size):
                batch = file_paths[i:i + batch_size]
                self.queue.put(("progress", i))
                self.queue.put(("status", f"Processing files {i+1} to {min(i+batch_size, total_files)} of {total_files}"))
                
                # Find duplicates in current batch
                duplicates = self.detector.find_duplicates(batch, threshold)
                
                # Update UI with results
                for file1, file2 in duplicates:
                    similarity = self.detector.compute_similarity(file1, file2)
                    self.queue.put(("result", (file1, file2, similarity)))
            
            self.queue.put(("complete", None))
            
        except Exception as e:
            self.queue.put(("error", str(e)))
            
    def check_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == "progress_max":
                    self.progress['maximum'] = data
                elif msg_type == "progress":
                    self.progress['value'] = data
                elif msg_type == "status":
                    self.progress_label.configure(text=data)
                elif msg_type == "result":
                    file1, file2, similarity = data
                    # Show full paths in the tree
                    self.tree.insert('', 'end', values=(
                        file1,  # Full path for File 1
                        file2,  # Full path for File 2
                        f"{similarity:.2f}",
                        file1,  # Store full paths for operations
                        file2
                    ))
                elif msg_type == "error":
                    messagebox.showerror("Error", data)
                    self.search_completed()
                elif msg_type == "complete":
                    self.search_completed()
                    
        except queue.Empty:
            pass
            
        self.root.after(100, self.check_queue)
            
    def search_completed(self):
        self.progress['value'] = self.progress['maximum']
        self.search_button.configure(state='normal')
        self.status_var.set("Search completed")
        self.progress_label.configure(text="Search completed")
        
def main():
    root = tk.Tk()
    app = DuplicateFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 