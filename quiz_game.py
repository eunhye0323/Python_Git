import json

# class Quiz:
#     def __init__(self, question, choices, answer):
#         self.question = question
#         self.choices = choices
#         self.answer = answer
    
#     def get_quiz_list(quiz_list):
#         quizzes = []
#         for quiz_data in quiz_list:
#             question = quiz_data["question"]
#             choices = quiz_data["options"]
#             answer = quiz_data["answer"]
#             quizzes.append(Quiz(question, choices, answer))
#         return quizzes
        
#     def print_quizzes(self):
#         print(self.question)
#         for i, choice in enumerate(self.choices):
#             print(f"{i + 1}. {choice}")
            
#     def check_answer(self, user_answer):
#         return user_answer == self.answer        
    
class QuizGame:
    # def __init__(self):
    #     with open("quiz_list.json", "r", encoding="utf-8") as f:
    #         self.quiz_list = json.load(f)
    #     self.quizzes = Quiz.get_quiz_list(self.quiz_list)
    #     self.score = 0

    # def print_quizzes(self, quiz):
    #     print(quiz.question)
    #     for i, choice in enumerate(quiz.choices):
    #         print(f"{i + 1}. {choice}")
                    
    def start(self):
        with open("quiz_list.json", "r", encoding="utf-8") as f:
            quiz_list = json.load(f)
                    
        for quiz in quiz_list:
            print("Q : " + quiz["question"])
            for i, option in enumerate(quiz["options"], start=1):
                print(f"{i}. {option}")

            user_answer = int(input("Enter your answer (1-4): ")) - 1
            
            #self.print_quizzes(quiz)
            #user_answer = int(input("Enter your answer (1-4): ")) - 1
            #if quiz.check_answer(user_answer):
                #self.score += 1
        #print(f"Your final score is: {self.score}/{len(self.quizzes)}")
             
def main():
    max_score = 0
    ans_count = 0
    
    # 프로그램 재시작 후 데이터 유지
    with open("state.json", "r", encoding="utf-8") as f:
        quiz_list = json.load(f)   
        
    # 프로그램 실행 시 메뉴 출력
    print("퀴즈 게임 메뉴:")
    print("1. 퀴즈 풀기")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 점수 확인")
    print("5. 종료 \n")

    # 사용자가 기능 선택과 종료를 선택할 수 있도록 함
    choice = input("Enter your choice (1-5): ")
    
    if choice == "1":
        QuizGame().start()
        
    elif choice == "2":
        print("새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ")
        
        options = []
        for i in range(4):
            option = input(f"선택지 {i+1}를 입력하세요: ")
            options.append(option)
        answer = int(input("정답 번호를 입력하세요 (1-4): ")) - 1
        
        
    elif choice == "3":
        print("퀴즈 목록을 표시합니다.")
        print("등록된 퀴즈 목록 (총 {}개):".format(len(quiz_list)))
        for i, quiz in enumerate(quiz_list, start=1):
            print(f"{i}. {quiz['question']}")

    elif choice == "4":
        print("점수를 확인합니다.")
        print("최고 점수: {}점 ({}문제 중 {}문제 정답)".format(max_score, len(quiz_list), ans_count))

    elif choice == "5":
        print("퀴즈 게임을 종료합니다.")
    
    # 잘못된 입력에 대한 처리
    else:
        print("잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")

if __name__ == "__main__":
    main()