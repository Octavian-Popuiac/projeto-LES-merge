
// Represents the structure of a Project
export interface Project {
    id: number;
    name: string;
  }
  
  // Represents a Perspective associated with a Project
  export interface Perspective {
    id: number;
    project: Project;
    project_id: number; 
  }
  
  // Represents the base question for a perspective
  export interface PerspectiveQuestionBase {
    id: number;
    question_text: string;
  }
  
  // Represents a PerspectiveQuestion linked to a Perspective and a base question
  export interface PerspectiveQuestion {
    id: number;
    perspective: Perspective;
    perspective_id: number; 
    question: PerspectiveQuestionBase;
    question_id: number; 
  }
  
  // Represents a member's response to a question in a perspective
  export interface PerspectiveMember {
    id: number;
    perspective: Perspective;
    perspective_id: number; 
    user: { username: string }; 
    user_id: number; 
    question: PerspectiveQuestion;
    question_id: number; 
    value: string;
}