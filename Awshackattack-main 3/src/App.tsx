import { useState } from 'react';
import { Bell, Mail, Search, RotateCcw, Lightbulb, Plus, X } from 'lucide-react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Separator } from './components/ui/separator';
import { Badge } from './components/ui/badge';
import { toast } from 'sonner@2.0.3';
import { Toaster } from './components/ui/sonner';
import logo from 'figma:asset/5f77e973ca708199b8cf85b2969fa3ec0a798977.png';

export default function App() {
  const [courseNames, setCourseNames] = useState(['', '', '', '']);
  const [quarter, setQuarter] = useState('');
  const [dayOfWeek, setDayOfWeek] = useState('');
  const [classTime, setClassTime] = useState('');
  const [professorPreferences, setProfessorPreferences] = useState('');
  const [submittedData, setSubmittedData] = useState<{
    courseNames: string[];
    quarter: string;
    dayOfWeek: string;
    classTime: string;
    professorPreferences: string;
  } | null>(null);

  const addCourseInput = () => {
    setCourseNames([...courseNames, '']);
  };

  const removeCourseInput = (index: number) => {
    if (courseNames.length > 1) {
      const newCourseNames = courseNames.filter((_, i) => i !== index);
      setCourseNames(newCourseNames);
    }
  };

  const updateCourseName = (index: number, value: string) => {
    const newCourseNames = [...courseNames];
    newCourseNames[index] = value;
    setCourseNames(newCourseNames);
  };

  const clearForm = () => {
    setCourseNames(['', '', '', '']);
    setQuarter('');
    setDayOfWeek('');
    setClassTime('');
    setProfessorPreferences('');
    setSubmittedData(null);
  };

  const handleRedo = () => {
    const confirmRedo = window.confirm(
      '🔄 Starting Fresh\n\nThis will clear all your current entries.\n\nConsider:\n• Want to add a different course?\n• Need to change the schedule?\n• Want to update professor information?\n\nReady to start over?'
    );
    
    if (confirmRedo) {
      clearForm();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      setTimeout(() => {
        toast.success('✨ Form cleared! You can now add a new course.');
      }, 400);
    }
  };

  const handleSubmit = () => {
    const filledCourses = courseNames.filter(name => name.trim() !== '');
    
    if (filledCourses.length === 0 || !quarter || !dayOfWeek || !classTime) {
      toast.error('⚠️ Please complete all required fields before adding to schedule.');
      return;
    }

    // Save submitted data
    setSubmittedData({
      courseNames: filledCourses,
      quarter,
      dayOfWeek,
      classTime,
      professorPreferences,
    });

    // Show success message
    toast.success('✅ Schedule added to calendar!');
    
    // Scroll to the submitted section
    setTimeout(() => {
      const element = document.getElementById('submitted-schedule');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #B30738 0%, #8B0000 100%)' }}>
      <Toaster />
      
      {/* Top Navigation */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-lg shadow-lg">
        <div className="px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo Section */}
            <div className="flex items-center gap-3 cursor-pointer transition-transform hover:scale-105">
              <img 
                src={logo} 
                alt="Classify Logo" 
                className="w-12 h-12"
              />
              <div
                className="bg-gradient-to-br from-[#B30738] to-[#8B0000] bg-clip-text text-transparent"
                style={{ fontSize: '22px', fontWeight: 700 }}
              >
                Classify
              </div>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-[500px] mx-10 relative hidden md:block">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <Input
                type="text"
                placeholder="Search courses, professors..."
                className="w-full pl-12 pr-5 py-3 rounded-full border-2 border-gray-200 bg-white shadow-sm transition-all focus:border-[#B30738] focus:shadow-lg focus:shadow-[#B30738]/20"
              />
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <div className="relative w-11 h-11 rounded-full flex items-center justify-center cursor-pointer transition-all bg-gray-100 hover:bg-gradient-to-br hover:from-[#B30738] hover:to-[#8B0000] hover:text-white hover:scale-110">
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center text-white border-2 border-white" style={{ fontSize: '10px', fontWeight: 700 }}>
                  3
                </span>
              </div>
              <div className="w-11 h-11 rounded-full flex items-center justify-center cursor-pointer transition-all bg-gray-100 hover:bg-gradient-to-br hover:from-[#B30738] hover:to-[#8B0000] hover:text-white hover:scale-110">
                <Mail size={20} />
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="py-10 px-5">
        <div className="max-w-[800px] mx-auto">
          {/* Header */}
          <div className="text-center mb-10 animate-fade-in">
            <h1 className="text-white mb-3 tracking-tight" style={{ fontSize: '48px', fontWeight: 800, textShadow: '0 4px 20px rgba(0,0,0,0.2)', letterSpacing: '-1px' }}>
              Course Scheduler
            </h1>
            <p className="text-white/95" style={{ fontSize: '18px' }}>
              Make your schedule for next quarter
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-white rounded-3xl p-12 shadow-2xl mb-6 animate-slide-up relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5" style={{ background: 'linear-gradient(90deg, #B30738 0%, #8B0000 50%, #B30738 100%)' }} />

            {/* Course Details Section */}
            <div className="mb-10">
              <div className="mb-7 relative pl-6">
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-[#B30738] to-[#8B0000] rounded-full" />
                <div className="flex items-center gap-3 mb-2">
                  <span style={{ fontSize: '28px' }}>📚</span>
                  <h2 className="text-gray-900" style={{ fontSize: '26px', fontWeight: 700 }}>
                    List of Courses
                    <span className="text-red-500 ml-1">*</span>
                  </h2>
                </div>
                <p className="text-gray-600" style={{ fontSize: '15px', lineHeight: '1.6' }}>
                  Add your courses (add multiple if needed)
                </p>
              </div>

              <div className="space-y-4">
                <Label className="text-gray-700 mb-3 block">
                  Course Names
                </Label>
                {courseNames.map((courseName, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <Input
                      type="text"
                      value={courseName}
                      onChange={(e) => updateCourseName(index, e.target.value)}
                      placeholder="Enter course name..."
                      className="flex-1 p-4 border-4 border-gray-200 rounded-2xl bg-gray-50 transition-all hover:border-[#B30738] hover:bg-white focus:ring-4 focus:ring-[#B30738]/10"
                    />
                    {courseNames.length > 1 && (
                      <Button
                        type="button"
                        onClick={() => removeCourseInput(index)}
                        variant="outline"
                        className="p-3 h-auto border-4 border-gray-200 rounded-2xl hover:border-red-400 hover:bg-red-50 hover:text-red-600 transition-all"
                      >
                        <X size={20} />
                      </Button>
                    )}
                  </div>
                ))}
                <Button
                  type="button"
                  onClick={addCourseInput}
                  variant="outline"
                  className="w-full p-4 border-4 border-dashed border-gray-300 rounded-2xl bg-gray-50 hover:border-[#B30738] hover:bg-red-50 hover:text-[#B30738] transition-all"
                >
                  <Plus size={20} className="mr-2" />
                  Add Another Course
                </Button>
              </div>
            </div>

            {/* Class Schedule Section */}
            <div className="mb-10">
              <div className="mb-7 relative pl-6">
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-[#B30738] to-[#8B0000] rounded-full" />
                <div className="flex items-center gap-3 mb-2">
                  <span style={{ fontSize: '28px' }}>📅</span>
                  <h2 className="text-gray-900" style={{ fontSize: '26px', fontWeight: 700 }}>
                    Class Schedule
                    <span className="text-red-500 ml-1">*</span>
                  </h2>
                </div>
                <p className="text-gray-600" style={{ fontSize: '15px', lineHeight: '1.6' }}>
                  When do you want to have class?
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-6 mb-7">
                <div>
                  <Label htmlFor="quarter" className="text-gray-700 mb-3 block">
                    Quarter
                  </Label>
                  <Select value={quarter} onValueChange={setQuarter}>
                    <SelectTrigger className="w-full p-4 border-4 border-gray-200 rounded-2xl bg-gray-50 transition-all hover:border-[#B30738] hover:bg-white focus:ring-4 focus:ring-[#B30738]/10">
                      <SelectValue placeholder="Select quarter..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fall">Fall</SelectItem>
                      <SelectItem value="winter">Winter</SelectItem>
                      <SelectItem value="spring">Spring</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="dayOfWeek" className="text-gray-700 mb-3 block">
                    Day of Week
                  </Label>
                  <Select value={dayOfWeek} onValueChange={setDayOfWeek}>
                    <SelectTrigger className="w-full p-4 border-4 border-gray-200 rounded-2xl bg-gray-50 transition-all hover:border-[#B30738] hover:bg-white focus:ring-4 focus:ring-[#B30738]/10">
                      <SelectValue placeholder="Select day..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monday">Monday</SelectItem>
                      <SelectItem value="tuesday">Tuesday</SelectItem>
                      <SelectItem value="wednesday">Wednesday</SelectItem>
                      <SelectItem value="thursday">Thursday</SelectItem>
                      <SelectItem value="friday">Friday</SelectItem>
                      <SelectItem value="mw">Monday/Wednesday</SelectItem>
                      <SelectItem value="mwf">Monday/Wednesday/Friday</SelectItem>
                      <SelectItem value="tth">Tuesday/Thursday</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="classTime" className="text-gray-700 mb-3 block">
                    Time of day
                  </Label>
                  <Select value={classTime} onValueChange={setClassTime}>
                    <SelectTrigger className="w-full p-4 border-4 border-gray-200 rounded-2xl bg-gray-50 transition-all hover:border-[#B30738] hover:bg-white focus:ring-4 focus:ring-[#B30738]/10">
                      <SelectValue placeholder="Select time..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="morning">Morning</SelectItem>
                      <SelectItem value="afternoon">Afternoon</SelectItem>
                      <SelectItem value="evening">Evening</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Professor Preferences Section */}
            <div className="mb-10">
              <div className="mb-7 relative pl-6">
                <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-[#B30738] to-[#8B0000] rounded-full" />
                <div className="flex items-center gap-3 mb-2">
                  <span style={{ fontSize: '28px' }}>👨‍🏫</span>
                  <h2 className="text-gray-900" style={{ fontSize: '26px', fontWeight: 700 }}>
                    What do you want in a professor?
                  </h2>
                </div>
                <p className="text-gray-600" style={{ fontSize: '15px', lineHeight: '1.6' }}>
                  Enter 2-3 sentences
                </p>
              </div>

              <div className="mb-7">
                <Textarea
                  value={professorPreferences}
                  onChange={(e) => setProfessorPreferences(e.target.value)}
                  placeholder="Describe your ideal professor..."
                  className="w-full p-4 border-4 border-gray-200 rounded-2xl bg-gray-50 transition-all hover:border-[#B30738] hover:bg-white focus:ring-4 focus:ring-[#B30738]/10 min-h-[120px] resize-none"
                />
              </div>

              <Separator className="my-8 bg-gradient-to-r from-transparent via-[#B30738] to-transparent h-0.5" />

              {/* Info Box */}
              <div className="relative overflow-hidden rounded-2xl border-4 border-yellow-400 p-6" style={{ background: 'linear-gradient(135deg, #fff9e6 0%, #ffe9a6 100%)' }}>
                <div className="absolute -right-5 -top-8 opacity-10" style={{ fontSize: '120px' }}>
                  💡
                </div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-2 text-yellow-800" style={{ fontSize: '18px', fontWeight: 700 }}>
                    <Lightbulb className="text-yellow-800" size={20} />
                    Need to Start Over?
                  </div>
                  <p className="text-yellow-900" style={{ fontSize: '15px', lineHeight: '1.7' }}>
                    If you'd like to change your course selections or schedule, use the "Redo" button below. This will clear all your entries so you can add different courses with fresh information.
                  </p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-5 justify-center mt-10">
              <Button
                onClick={() => {}}
                className="px-10 py-4 rounded-2xl bg-gradient-to-r from-red-500 to-red-600 text-white hover:shadow-xl hover:shadow-red-500/50 hover:-translate-y-1 hover:scale-105 transition-all duration-300 border-0"
              >
                Generate Schedule
              </Button>

              <Button
                onClick={handleRedo}
                className="px-10 py-4 rounded-2xl bg-gradient-to-r from-red-400 to-red-500 text-white hover:shadow-xl hover:shadow-red-500/50 hover:-translate-y-1 hover:scale-105 transition-all duration-300 border-0"
              >
                <RotateCcw className="mr-2 transition-transform group-hover:rotate-[-360deg] duration-500" size={20} />
                Redo
              </Button>

              <Button
                onClick={handleSubmit}
                className="px-10 py-4 rounded-2xl bg-gradient-to-r from-[#B30738] to-[#8B0000] text-white hover:shadow-xl hover:shadow-[#B30738]/50 hover:-translate-y-1 hover:scale-105 transition-all duration-300 border-0"
              >
                Add to Google Calendar
              </Button>
            </div>
          </div>

          {/* Submitted Schedule Display */}
          {submittedData && (
            <div id="submitted-schedule" className="max-w-[800px] mx-auto mt-8 animate-slide-up">
              <div className="bg-white rounded-3xl p-12 shadow-2xl mb-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-1.5" style={{ background: 'linear-gradient(90deg, #4CAF50 0%, #2E7D32 50%, #4CAF50 100%)' }} />
                
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-green-100 to-green-200 mb-4">
                    <span style={{ fontSize: '40px' }}>✅</span>
                  </div>
                  <h2 className="text-gray-900" style={{ fontSize: '32px', fontWeight: 800 }}>
                    Schedule Created!
                  </h2>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(40px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.6s ease;
        }

        .animate-slide-up {
          animation: slide-up 0.6s ease;
        }
      `}</style>
    </div>
  );
}
