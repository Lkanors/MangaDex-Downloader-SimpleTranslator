import boxes, crop, create_new_images as ci
import db_manager as db
import ollama, os
class Unify:
    def __init__(self, lang, target_lang, mode, model, output, folder_path, manga_id):
        self.id=manga_id
        self.output=output
        self.lang=lang
        self.target_lang=target_lang
        self.mode=mode
        self.folder_path=folder_path
        # self.paddle=boxes.create('en', folder_path)
        self.model=model
        print(self.folder_path)
        print(self.output)

    def translate_images(self):
        # self.ollama_text=self.recognized_text.process(self.folder_path)
        self.paddle=boxes.create('en', self.folder_path)
        self.paddle_text=self.paddle()
        # print(self.ollama_text)
        # print([i[2] for i in self.paddle_text])
        print(self.paddle_text)
        # dt.draw_test(self.paddle_text, "output")
    def comparison(self):
        client_ol=ollama.Client()
        num_ch=""
        for x, block in enumerate(self.paddle_text):
            temp=crop.crop_to_temp(block[0], block[1])
            
            # ollama_part=[i[1] for i in self.ollama_text if i[0] in self.paddle_text[x][0]][0]
            if self.mode!='context':
                pass
                request=client_ol.chat(
                    model=self.model,
                    messages=[{'role': 'system', 'content':
                            f"""
    You are professional manga translator to {self.target_lang}.
    Rules:
    Output ONLY correctly translate of input image in one line. Nothing else.
    Do NOT output any tags like a <start_of_image>, <end_of_image> (IMPORTANT)
    Translate ANYTHING, do NOT output text in {self.lang} (VERY IMPORTANT)
    """},
    {'role': 'user','content': f"", 'images': [temp],}],
                    options={
        'temperature': 0.25
    }, think=False  )
                
                
#             )
#             print("Text extracted")
            # if num_ch!=block[0]:
            #     ol_save=client_ol.chat(
            #         model=self.model,
            #         messages=[{'role': 'user','content': f"""Return only text from this image. Nothing else""", "images": [block[0]]}]
            #     )
            #     print('435fwfv0---------=====')
            #     print(ol_save.message.content)
            #     ollama_part=ol_save.message.content
            else:
    #             print('context')
    #             request=client_ol.chat(
    #                 model=self.model,
    #                 messages=[{'role': 'system','content': f"""
    # You are an expert manga translator.

    # Translate ONLY the text in the FIRST image into {self.target_lang}.
    
    # The SECOND image is context ONLY. Use it only to resolve ambiguous names, pronouns, or incomplete dialogue. Never translate any text from the second image.

    # Rules:
    # - Translate only text from the first image.
    # - Preserve the original reading order.
    # - Keep tone, personality, and meaning natural.
    # - Do not add, omit, summarize, or explain.
    # - Do not output the original {self.lang} text.
    # - Do not output markdown, image tags, or any extra text.
    # - Do not write tags like a <start_of_image>, <end_of_image>
    # Output ONLY the translation in {self.target_lang}.
    # """},{"role": "user", "content": "Translate the text from first image", "images": [temp, block[0]]}],
    #                 think=False
    #                     options={
    #     'temperature': 0.2
    # }                    
                # )
                request=client_ol.chat(
                        model=self.model,
                        messages=[{'role': 'user','content': f"""You are an expert manga translator to {self.target_lang}.

    Your task is to translate ONLY the dialogue and text that appears in the FIRST image.

    The SECOND image is provided ONLY as context to resolve ambiguous pronouns, names, references, or incomplete speech bubbles. NEVER translate any text from the second image.

    If the text in the image is unclear, output "..."

    Output only translated first image to {self.target_lang}. Nothing else. Do not output {self.lang} text.""", "images": [temp, block[0]]}],
    think=False,
    options={"temperature": 0.25})
            crop.cleanup_temp(temp)
            print(f"Translate: {request.message.content}")
            # text_processed=request.message.content.replace('\n<end_of_image>', ';;;').replace('<start_of_image>\n', ';;;').replace('<end_of_image>', ';;;').replace('<start_of_image>', ';;;')
            self.paddle_text[x][2]=request.message.content
            if block[0]!=num_ch:
                ci.create([i for i in self.paddle_text if i[0]==num_ch], self.folder_path.replace(self.output, f"{self.output}_translated"))
            num_ch=block[0]
        ci.create([i for i in self.paddle_text if i[0]==num_ch], self.output)
        db.change_translated_status(self.id, self.output, True)
            
    def start_translation(self):
        print("Starting translation...")
        print(f"{self.lang} to {self.target_lang}")
        self.translate_images()
        self.comparison()
# a=Unify("English", "Russian", "context", model_list[1], "output", "Konna Toki Dakara Iwasetekure")
# a.translate_images()
# a.comparison()

    