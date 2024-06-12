import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from googletrans import Translator
from PIL import Image, ImageTk

class PDFReader:
    """
    PDFReader class for creating a simple PDF reader with translation functionality.

    Args:
        root: Tkinter root object to create the application window.

    Attributes:
        root (tk.Tk): Tkinter root object representing the application window.
        frame (tk.Frame): Frame for containing the canvas and scrollbar.
        canvas (tk.Canvas): Canvas widget for displaying PDF pages.
        scrollbar (tk.Scrollbar): Vertical scrollbar linked to the canvas.
        pdf_frame (tk.Frame): Inner frame to hold the PDF pages.
        translator (Translator): Google Translator object for translation.
        pdf_document (fitz.Document): PDF document object loaded for reading.
        current_page (int): Index of the currently displayed page.
        text_positions (list): List of tuples containing text positions on the page.
        page_images (list): List of images corresponding to each page.

    Methods:
        load_pdf(): Load a PDF file and display its first page.
        display_page(page_number): Display the specified page of the PDF document.
        on_frame_resize(event): Handle resizing of the canvas frame.
        on_canvas_resize(event): Handle resizing of the canvas.
        on_click(event): Handle mouse click events to show translations.
        find_word_at_position(x, y): Find the word at the specified canvas coordinates.
        translate_word(word): Translate the given word to Hindi.
        prev_page(): Display the previous page of the PDF document.
        next_page(): Display the next page of the PDF document.
    """

    def __init__(self, root):
        # Initialize root window
        self.root = root
        self.root.title("PDF Reader with Translation")

        # Create frame for canvas and scrollbar
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas widget
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add vertical scrollbar linked to the canvas
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create inner frame to hold PDF pages
        self.pdf_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.pdf_frame, anchor="nw")

        # Bind canvas and inner frame for resizing
        self.pdf_frame.bind("<Configure>", self.on_frame_resize)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Bind mouse click event
        self.canvas.bind("<Button-1>", self.on_click)

        # Initialize Google Translator
        self.translator = Translator()

        # Initialize attributes
        self.pdf_document = None
        self.current_page = 0
        self.text_positions = []
        self.page_images = []

        # Create navigation buttons
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.prev_button = tk.Button(self.nav_frame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(self.nav_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT)

        # Load PDF file
        self.load_pdf()

    def load_pdf(self):
        """
        Open a file dialog to select a PDF file and load it for reading.
        """
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            messagebox.showerror("Error", "No file selected")
            return

        self.pdf_document = fitz.open(file_path)
        self.display_page(self.current_page)

    def display_page(self, page_number):
        """
        Display the specified page of the PDF document on the canvas.

        Args:
            page_number (int): Index of the page to display.
        """
        if self.pdf_document is None or page_number < 0 or page_number >= len(self.pdf_document):
            return

        self.canvas.delete("all")

        page = self.pdf_document[page_number]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_tk = ImageTk.PhotoImage(img)

        self.canvas.image = img_tk
        self.canvas.create_image(0, 0, anchor="nw", image=img_tk)

        self.text_positions = page.get_text("words")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_frame_resize(self, event):
        """
        Handle resizing of the canvas frame.
        """
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_canvas_resize(self, event):
        """
        Handle resizing of the canvas.
        """
        self.canvas.itemconfig(self.canvas.create_window((0, 0), window=self.pdf_frame, anchor="nw"))

    def on_click(self, event):
        """
        Handle mouse click events to show translations.
        """
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        word = self.find_word_at_position(x, y)
        if word:
            translation = self.translate_word(word)
            if translation:
                messagebox.showinfo("Translation", f"{word} -> {translation}")

    def find_word_at_position(self, x, y):
        """
        Find the word at the specified canvas coordinates.

        Args:
            x (float): X-coordinate on the canvas.
            y (float): Y-coordinate on the canvas.

        Returns:
            str: Text corresponding to the word found at the given coordinates.
        """
        for word in self.text_positions:
            x0, y0, x1, y1, text, block_no, line_no, word_no = word
            if x0 <= x <= x1 and y0 <= y <= y1:
                return text
        return None

    def translate_word(self, word):
        """
        Translate the given word to Hindi.

        Args:
            word (str): English word to be translated.

        Returns:
            str: Translated word in Hindi.
        """
        try:
            translated = self.translator.translate(word, src='en', dest='hi')
            return translated.text
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed: {str(e)}")
            return None

    def prev_page(self):
        """
        Display the previous page of the PDF document.
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)

    def next_page(self):
        """
        Display the next page of the PDF document.
        """
        if self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.display_page(self.current_page)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReader(root)
    root.mainloop()

