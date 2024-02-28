import tkinter as tk
from tkinter import filedialog
from azure.storage.blob import BlobServiceClient
import os
import time
from tkinter.ttk import Treeview
from tkinter import simpledialog, messagebox
from tkinter import ttk


class AzureStorageExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure Storage Explorer")

        # Azure Storage connection
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName=snowflakeazuredemo103;AccountKey=VoHCO6c56mSSGnGf0EzaNgv9n8y1KeV+8a7qBHqNgbvCfQRYHiPvJea38bD6ZVsGYaklkZ0Fzbet+AStRDyCXg==;EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Container name
        self.container_name = "snowflake-demo"
        self.path = "/"
        self.navigate = []

        # Track copied items
        self.copied_items = []

        # Frame for path input
        self.path_frame = tk.Frame(root)
        self.path_frame.pack(side=tk.TOP, fill=tk.X)

        # Top frame for buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill=tk.X)

        # Previous and Next buttons
        self.prev_button = tk.Button(self.button_frame, text="⏪", command=self.prev_files, bg="blue")
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.button_frame, text="⏩", command=self.next_files , bg="blue")
        self.next_button.pack(side=tk.LEFT)

        

        # Upload and delete buttons
        self.upload_button = tk.Button(self.button_frame, text="📤", command=self.upload_file)
        self.upload_button.pack(side=tk.LEFT)        

        # Label for the path entry
        self.path_label = tk.Label(self.button_frame, text="Path:" , bg="lightblue", fg="blue", cursor="hand2")
        self.path_label.pack(side=tk.LEFT)
        self.path_label.bind("<Button-1>", self.navigate_to_folder)

        # List of paths for dropdown
        self.path_options = ['/','/dipak/', '/dipak/tiwari/', '/dipak/tiwari/kumar/']
        

        # String variable to store selected path
        self.selected_path = tk.StringVar(root)
        self.selected_path.set(self.path_options[0])  # Set default path

        # Combobox for selecting path
        self.path_combobox = ttk.Combobox(self.button_frame, textvariable=self.selected_path, values=self.path_options)
        self.path_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.path_combobox.bind("<<ComboboxSelected>>", self.update_path_entry)

        self.submit_path_button = tk.Button(self.button_frame, text="➡️", command=self.go_to_path)
        self.submit_path_button.pack(side=tk.LEFT)

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📋" +  "Copy", command=self.copy_file)
        self.context_menu.add_command(label="📥" +  "Paste", command=self.paste_file)
        self.context_menu.add_command(label="⬇️" +  "Download", command=self.download_file)
        self.context_menu.add_command(label="🗑️" +  "Delete", command=self.delete_file)
        self.context_menu.add_command(label="🔄" + "Rename", command=self.rename_file)



        # File list frame
        self.file_frame = tk.Frame(root)
        self.file_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # File list treeview
        self.file_tree = Treeview(self.file_frame, columns=("Name", "Modified Date", "Size"), selectmode="browse")
        self.file_tree.heading("Name", text="Name")
        self.file_tree.heading("Modified Date", text="Modified Date")
        self.file_tree.heading("Size", text="Size")
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        # Bind right-click event to file listbox
        self.file_tree.bind("<Button-3>", self.popup)


        # Bind double-click event to file listbox
        self.file_tree.bind('<Double-Button-1>', self.on_file_double_click)


        # Populate files initially
        self.populate_files()

    def popup_path_entry(self, event):
        # Display context menu for path entry
        self.path_context_menu.tk_popup(event.x_root, event.y_root)

    def update_path_entry(self, event):
        # Update path entry when a path is selected from the combobox
        selected_path = self.selected_path.get()
        self.path = selected_path  # Update path variable
        self.populate_files()  # Update file list
  
    def go_to_path(self):
        # Get the path from the entry widget
        path = self.selected_path.get()
        # Navigate to the specified path
        self.path = path
        self.populate_files() 

    def update_path_label(self):
        # Clear existing labels
        for widget in self.path_frame.winfo_children():
            widget.destroy()

        # Split the path into individual folders
        folders = self.path.split("/")
        folders = [folder for folder in folders if folder]  # Remove empty strings

        # Create clickable labels for each folder
        for i, folder in enumerate(folders):
            label = tk.Label(
                self.path_frame,
                text=folder,
                fg="blue",  # Set color to blue for clickable effect
                cursor="hand2"  # Set cursor to hand pointer
            )
            label.bind("<Button-1>", lambda event, folder=folder: self.go_to_folder(folder))
            label.pack(side=tk.LEFT)

            # Add a slash after each folder except the last one
            if i < len(folders) - 1:
                slash_label = tk.Label(self.path_frame, text=">")
                slash_label.pack(side=tk.LEFT)

    def go_to_folder(self, folder):
        # Navigate to the specified folder 
        fol_name = []
        for x in self.path.split("/"):
            if folder == x:
                 fol_name.append(x)
                 break
            else:
                fol_name.append(x)

        self.path = "/".join(fol_name) + "/" 
        self.selected_path.set(self.path)
        self.populate_files()

    def navigate_to_folder(self, event):
        # Get the clicked folder name
        folder_name = self.path_label.cget("text")
        # Update the path and populate files
        self.path = os.path.dirname(self.path.rstrip("/" + folder_name)) + "/"
        self.populate_files()

    # Implement methods to handle these events
    def popup(self, event):
        # Get the item under the cursor
        item = self.file_tree.identify_row(event.y)
        # If an item is selected, display the context menu
        if item:
            self.file_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

                
    def on_file_double_click(self, event):
        # Get the selected item
        selected_item = self.file_tree.selection()[0]  # Assuming single selection
        # Get the text of the selected item
        item_text = self.file_tree.item(selected_item, "text")
        # Update the path with the selected item
        self.path += item_text + '/'
        # Set the updated path in the path entry widget
        self.selected_path.set(self.path)
        # Populate files at the new path
        self.populate_files()


    def copy_file(self):
        # Clear copied items list
        self.copied_items.clear()
        # Add selected items to copied items lists
        selected_items = self.file_tree.selection()
        for item in selected_items:
            file = self.file_tree.item(item, 'text')
            file_path = os.path.join(self.path, file)
            self.copied_items.append(file_path)

    def paste_file(self):
        container_client = self.blob_service_client.get_container_client(self.container_name)
        for item in self.copied_items:
            try:
                source_blob_path = item
                source_blob_client = container_client.get_blob_client(blob=source_blob_path)
                destination_blob_path = os.path.join(self.path, os.path.basename(item))
                destination_blob_client = container_client.get_blob_client(blob=destination_blob_path)
                destination_blob_client.start_copy_from_url(source_blob_client.url)
            except Exception as e:
                print(f"Error copying blob: {e}")
                # Handle the error appropriately, e.g., logging, displaying a message to the user, etc.
        self.populate_files()

    def rename_file(self):
        # Get selected file(s) from treeview
        selected_indices = self.file_tree.selection()
        if not selected_indices:
            messagebox.showwarning("No File Selected", "Please select a file to rename.")
            return

        # Prompt user for new file name
        new_name = simpledialog.askstring("Rename File", "Enter new name:")
        if not new_name:
            return  # User canceled the operation

        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            for index in selected_indices:
                # Get current file name
                old_name = self.file_tree.item(index, "text")
                # Form full paths for old and new files
                old_blob_path = os.path.join(self.path, old_name)
                new_blob_path = os.path.join(self.path, new_name)
                # Check if the new name already exists
                if container_client.get_blob_client(blob=new_blob_path).exists():
                    messagebox.showerror("Error", f"A file with the name '{new_name}' already exists.")
                    return
                # Get the blob client for the old file
                old_blob_client = container_client.get_blob_client(old_blob_path)
                # Copy the blob to the new name
                container_client.get_blob_client(new_blob_path).start_copy_from_url(old_blob_client.url)
                # Delete the original blob
                container_client.delete_blob(old_blob_path)
            
            # Refresh file list after renaming
            self.populate_files()
            messagebox.showinfo("Rename Complete", "File(s) renamed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_file(self):
        # Get selected file(s) from treeview
        selected_indices = self.file_tree.selection()
        if not selected_indices:
            messagebox.showwarning("No File Selected", "Please select a file to delete.")
            return

        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            for index in selected_indices:
                file_name = self.file_tree.item(index, "text")
                full_blob_path = os.path.join(self.path, file_name)  # Combine path and file name
                container_client.delete_blob(full_blob_path)  # Delete the blob using the full path

            # Refresh file list after deletion
            self.populate_files()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def download_file(self):
        # Get selected file(s) from treeview
        selected_indices = self.file_tree.selection()
        if not selected_indices:
            messagebox.showwarning("No File Selected", "Please select a file to download.")
            return

        # Select destination folder for downloading files
        destination_folder = filedialog.askdirectory()
        if not destination_folder:
            return  # User canceled the operation

        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            for index in selected_indices:
                file_name = self.file_tree.item(index, "text")
                full_blob_path = os.path.join(self.path, file_name)  # Combine path and file name
                blob_client = container_client.get_blob_client(blob=full_blob_path)  # Use full blob path
                # Define local file path for download
                local_file_path = os.path.join(destination_folder, file_name)
                # Download the blob to the local file path
                with open(local_file_path, "wb") as local_file:
                    download_stream = blob_client.download_blob()
                    local_file.write(download_stream.read())

            # Notify user when download is complete
            messagebox.showinfo("Download Complete", "Files downloaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def next_files(self):
        if self.navigate[0]:
            self.path = self.path + self.navigate[0] + '/'
            self.selected_path.set(self.path)
            self.navigate.pop(0)
            self.populate_files()
        else :
            self.populate_files()


    def prev_files(self):
        path_list = self.path.split('/')
        # Using the insert() method to add the new element at the first index
        self.navigate.insert(0, path_list[-2])
        self.path = "/".join([i for i in path_list[:-2]]) + '/'
        self.selected_path.set(self.path)
        self.populate_files()

    def upload_file(self):
        # Open file dialog to select file(s) to upload
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            # Upload each selected file to Azure Blob Storage
            container_client = self.blob_service_client.get_container_client(self.container_name)
            for file_path in file_paths:
                with open(file_path, "rb") as file:
                    original_blob_name = os.path.basename(file_path)
                    blob_name = self.path + original_blob_name  # Include folder path in blob name
                    blob_client = container_client.get_blob_client(blob_name)
                    # Check if blob already exists
                    if blob_client.exists():
                        # Append a timestamp to the blob name to make it unique
                        timestamp = int(time.time())
                        blob_name = f"{self.path}{original_blob_name}_{timestamp}"
                        blob_client = container_client.get_blob_client(blob_name)
                    # Upload the file with the modified blob name
                    container_client.upload_blob(name=blob_name, data=file)

            # Refresh file list after upload
            self.populate_files()


    def populate_files(self):
        # Clear existing items
        self.file_tree.delete(*self.file_tree.get_children())

        # List blobs in container
        container_client = self.blob_service_client.get_container_client(self.container_name)
        blobs = container_client.list_blobs(name_starts_with=self.path)


        files = []
        path_list = self.path.split('/')
        path_list.remove('')

        #blobs = ['461142.jpg','October.Sky.1999.720p.BluRay.x264.YIFY.srt' ,'dipak','dipak/Requirement_Analysis.docx','dipak/tiwari','dipak/tiwari/1703765126722.jpg','dipak/tiwari/kumar','dipak/tiwari/kumar/Her.English-WWW.MY-SUBS.CO.srt']
        for blob in blobs:
            parts = blob.name.split('/')
            if len(parts) > len(path_list)  :
                break
            else:
                files.append(parts[len(path_list) -1])
        
        for file in files:
            #self.file_listbox.insert(tk.END, file)

            file_path = os.path.join(self.path, file)
            blob_client = container_client.get_blob_client(blob=file_path)

            # Get file properties
            properties = blob_client.get_blob_properties()
            modified_date = properties.last_modified
            size = properties.size

            if file.find("."):
                file_name  = "📄" + ' ' + file
            else:
                file_name = "📁" + ' ' + file

            self.file_tree.insert("", "end", text=file, values=(file_name, modified_date, str(size) + ' KB'), tags=('hidden_text',))
            #self.file_tree.tag_configure('hidden_text', font=('', 0))  # Hide the text
            self.file_tree.column('#0', width=0, stretch=tk.NO)

        # Update the path detail box
        self.update_path_label()



def dipak():
    root = tk.Tk()
    app = AzureStorageExplorer(root)
    root.mainloop()

if __name__ == "__main__":
    dipak()
    dipak()
