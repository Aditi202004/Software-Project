import customtkinter as ctk

app = ctk.CTk()

checkbox1 = ctk.CTkCheckBox(app, text="CB1")
checkbox1.pack()
checkbox2 = ctk.CTkCheckBox(app, text="CB2")
checkbox2.pack()
app.mainloop()