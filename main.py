import customtkinter as ctk

root = ctk.CTk()

## Create Window
root.title("Tiktok Archiver")
root.geometry("500x300")
root.eval("tk::PlaceWindow . center")
root.resizable(False, False)
root.config(bg="black")

## Create Layout
left_frame = ctk.CTkFrame(root, width=280, height=300, fg_color="white", border_width=1, border_color="black", corner_radius=0)
left_frame.pack(padx=1, pady=1, side=ctk.LEFT)
left_frame.pack_propagate(False)

right_frame = ctk.CTkFrame(root, width=220, height=300, fg_color="white", border_width=1, border_color="black", corner_radius=0)
right_frame.pack(pady=1, side=ctk.RIGHT)
right_frame.pack_propagate(False)

## Top Titles
#-- Top Left
topleft_frame = ctk.CTkFrame(left_frame, height=30, border_width=1, border_color="black", fg_color="white", corner_radius=0)
topleft_frame.pack(fill="x", side=ctk.TOP,)
topleft_frame.pack_propagate(False)

# URL Textbox
ctk.CTkEntry(topleft_frame, width=230, text_color="black", fg_color="white", corner_radius=0, border_width=1).pack(pady=4, padx=(4,0),side=ctk.LEFT)

# Add Button
ctk.CTkButton(topleft_frame, border_width=1, text="Add", width=35, fg_color="white", text_color="black", corner_radius=0).pack(pady=4, padx=(0,4), side=ctk.RIGHT)

#-- Top Right
topright_frame = ctk.CTkFrame(right_frame, height=30, border_width=1, border_color="black", fg_color="white", corner_radius=0)
topright_frame.pack(fill="x", side=ctk.TOP,)
topright_frame.pack_propagate(False)

# Options Label
ctk.CTkLabel(topright_frame, text="Options", fg_color="transparent", text_color="black").pack(pady=1)

root.mainloop()