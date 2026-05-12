import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import sys

# --- Backend Logic ---
class UeSaveEditor:
    def __init__(self, uesave_filename="uesave"):
        # Detect if we are running as a bundled PyInstaller executable
        if getattr(sys, 'frozen', False):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            script_dir = sys._MEIPASS
        else:
            # Normal Python execution
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if os.name == 'nt' and not uesave_filename.endswith('.exe'):
            uesave_filename += '.exe'
            
        self.uesave_path = os.path.join(script_dir, uesave_filename)
        self.data = None

        if not os.path.exists(self.uesave_path):
            raise FileNotFoundError(f"Could not find uesave at: {self.uesave_path}")

    def load(self, sav_file_path):
        with open(sav_file_path, 'rb') as f:
            sav_bytes = f.read()

        result = subprocess.run(
            [self.uesave_path, 'to-json'],
            input=sav_bytes,
            capture_output=True
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            raise RuntimeError(f"uesave failed to parse the file:\n{error_msg}")

        json_string = result.stdout.decode('utf-8')
        self.data = json.loads(json_string)

    def save(self, output_path):
        json_bytes = json.dumps(self.data).encode('utf-8')

        result = subprocess.run(
            [self.uesave_path, 'from-json'],
            input=json_bytes,
            capture_output=True
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            raise RuntimeError(f"uesave failed to rebuild the file:\n{error_msg}")

        with open(output_path, 'wb') as f:
            f.write(result.stdout)


# --- GUI Logic ---
class GvasGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GVAS Save Editor - Tree View")
        self.root.geometry("900x750")
        
        try:
            self.editor = UeSaveEditor()
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.root.destroy()
            return

        self.current_file = None
        self.item_map = {} 
        
        # Search variables
        self.search_results = []
        self.current_search_index = -1

        self.create_widgets()

    def create_widgets(self):
        # --- Top Frame (File Buttons) ---
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)

        self.btn_load = tk.Button(top_frame, text="1. Load .sav File", command=self.load_file)
        self.btn_load.pack(side=tk.LEFT, padx=10)

        self.btn_save = tk.Button(top_frame, text="2. Save as .sav File", command=self.save_file, state=tk.DISABLED)
        self.btn_save.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(top_frame, text="Ready", fg="gray")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # --- Search Frame ---
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.entry_search = tk.Entry(search_frame)
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_search.bind("<Return>", lambda e: self.perform_search())
        
        self.btn_search = tk.Button(search_frame, text="Search", command=self.perform_search)
        self.btn_search.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = tk.Button(search_frame, text="Next", command=self.next_search_result, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT)

        self.lbl_search_status = tk.Label(search_frame, text="", fg="gray", width=15, anchor="w")
        self.lbl_search_status.pack(side=tk.LEFT, padx=10)

        # --- Middle Frame (Tree View) ---
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("Value",), selectmode="browse")
        self.tree.heading("#0", text="Property / Key")
        self.tree.heading("Value", text="Value")
        self.tree.column("#0", width=400, stretch=True)
        self.tree.column("Value", width=400, stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Bottom Frame (Edit Panel) ---
        edit_frame = tk.LabelFrame(self.root, text="Edit Selected Value", padx=10, pady=10)
        edit_frame.pack(fill=tk.X, padx=10, pady=10)

        self.lbl_selected_key = tk.Label(edit_frame, text="Select a value to edit...", font=("Arial", 10, "italic"))
        self.lbl_selected_key.pack(side=tk.TOP, anchor="w", pady=(0, 5))

        edit_subframe = tk.Frame(edit_frame)
        edit_subframe.pack(fill=tk.X)

        tk.Label(edit_subframe, text="New Value:").pack(side=tk.LEFT)
        self.entry_value = tk.Entry(edit_subframe, state=tk.DISABLED)
        self.entry_value.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.entry_value.bind("<Return>", lambda e: self.apply_edit())

        self.btn_update = tk.Button(edit_subframe, text="Update Value", command=self.apply_edit, state=tk.DISABLED)
        self.btn_update.pack(side=tk.RIGHT)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a GVAS Save File",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return

        self.status_label.config(text="Loading...", fg="blue")
        self.root.update()

        try:
            self.editor.load(filepath)
            self.current_file = filepath
            
            self.reset_search()
            self.tree.delete(*self.tree.get_children())
            self.item_map.clear()
            
            properties = self.editor.data.get("root", {}).get("properties", {})
            self.populate_tree("", "Properties", properties, self.editor.data.get("root", {}), "properties")
            
            self.btn_save.config(state=tk.NORMAL)
            self.status_label.config(text=f"Loaded: {os.path.basename(filepath)}", fg="green")
            
        except Exception as e:
            messagebox.showerror("Error Loading File", str(e))
            self.status_label.config(text="Error loading file", fg="red")

    def populate_tree(self, parent_node, key, value, parent_collection, collection_key):
        item_id = self.tree.insert(parent_node, "end", text=str(key))
        
        if isinstance(value, dict):
            for k, v in value.items():
                self.populate_tree(item_id, k, v, value, k)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                self.populate_tree(item_id, f"[{i}]", v, value, i)
        else:
            self.tree.set(item_id, "Value", str(value))
            self.item_map[item_id] = {
                'collection': parent_collection,
                'key': collection_key,
                'type': type(value)
            }

    # --- Search Functions ---
    def reset_search(self):
        self.search_results = []
        self.current_search_index = -1
        self.btn_next.config(state=tk.DISABLED)
        self.lbl_search_status.config(text="")
        self.entry_search.delete(0, tk.END)

    def perform_search(self):
        query = self.entry_search.get().lower()
        self.search_results = []
        self.current_search_index = -1
        
        if not query:
            self.lbl_search_status.config(text="Empty search")
            self.btn_next.config(state=tk.DISABLED)
            return

        def search_node(node):
            key_text = str(self.tree.item(node, "text")).lower()
            val_text = str(self.tree.set(node, "Value")).lower()
            
            if query in key_text or query in val_text:
                self.search_results.append(node)
                
            for child in self.tree.get_children(node):
                search_node(child)

        for child in self.tree.get_children(""):
            search_node(child)

        if self.search_results:
            self.btn_next.config(state=tk.NORMAL)
            self.next_search_result() 
        else:
            self.lbl_search_status.config(text="No matches found")
            self.btn_next.config(state=tk.DISABLED)

    def next_search_result(self):
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        node_id = self.search_results[self.current_search_index]

        parent = self.tree.parent(node_id)
        while parent:
            self.tree.item(parent, open=True)
            parent = self.tree.parent(parent)

        self.tree.selection_set(node_id)
        self.tree.see(node_id)
        self.on_tree_select(None)

        self.lbl_search_status.config(text=f"Match {self.current_search_index + 1} of {len(self.search_results)}")

    # --- Editing and Saving Functions ---
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item_id = selected[0]
        
        if item_id in self.item_map:
            self.entry_value.config(state=tk.NORMAL)
            self.btn_update.config(state=tk.NORMAL)
            
            item_text = self.tree.item(item_id, "text")
            self.lbl_selected_key.config(text=f"Editing: {item_text}")
            
            current_val = self.tree.set(item_id, "Value")
            self.entry_value.delete(0, tk.END)
            self.entry_value.insert(0, current_val)
        else:
            self.lbl_selected_key.config(text="Select a final value to edit...")
            self.entry_value.delete(0, tk.END)
            self.entry_value.config(state=tk.DISABLED)
            self.btn_update.config(state=tk.DISABLED)

    def apply_edit(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        item_id = selected[0]
        if item_id not in self.item_map:
            return

        new_val_str = self.entry_value.get()
        mapping = self.item_map[item_id]
        
        collection = mapping['collection']
        key = mapping['key']
        original_type = mapping['type']
        
        try:
            if original_type is bool:
                new_val = new_val_str.lower() in ('true', '1', 't', 'y', 'yes')
            elif original_type is int:
                new_val = int(new_val_str)
            elif original_type is float:
                new_val = float(new_val_str)
            else:
                new_val = new_val_str 
        except ValueError:
            messagebox.showerror("Type Error", f"Cannot convert '{new_val_str}' to {original_type.__name__}")
            return
            
        collection[key] = new_val
        self.tree.set(item_id, "Value", str(new_val))
        self.status_label.config(text="Value updated! Don't forget to click 'Save as'.", fg="#b8860b")

    def save_file(self):
        if not self.current_file:
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Modified GVAS File",
            defaultextension=".sav",
            initialfile=os.path.basename(self.current_file),
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if not save_path:
            return

        self.status_label.config(text="Saving...", fg="blue")
        self.root.update()

        try:
            self.editor.save(save_path)
            messagebox.showinfo("Success", f"File successfully saved to:\n{save_path}")
            self.status_label.config(text="Save Complete!", fg="green")
            
        except Exception as e:
            messagebox.showerror("Error Saving File", str(e))
            self.status_label.config(text="Error saving file", fg="red")

# --- Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GvasGuiApp(root)
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.mainloop()