from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from teacher.models import course, session, teacher
from .models import student, project, file, Message
from customuser.models import user_type
from django.core.files.storage import FileSystemStorage
from .forms import fileform
from django.core.mail import EmailMessage
import os
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your views here.


def shome(request):
    if request.user.is_authenticated and user_type.objects.get(user=request.user).is_student:
        # Gets project details and creates a project.
        if request.method == 'POST':
            project_title = request.POST.get('project-title')
            group_name = request.POST.get('group-name')
            course_code = course.objects.get(course_code=request.POST.get('course-list'))
            session_val = session.objects.get(session_id=request.POST.get('session-list'))
            project_id = project_title + session_val.batch + session_val.course_code.course_code

            member_data_string = request.POST.get('my_data')
            print("this is the name:", member_data_string)
            members = member_data_string.split(',')
            member_reg = []
            member_rol = []
            for val in members:
                reg = ""
                for c in val:
                    if c != '-':
                        reg = reg + c
                    else:
                        reg = reg.strip()
                        print("roll no.",reg,"this")
                        member_rol.append(reg)
                        member_reg.append(student.objects.get(reg_number=reg))
                        break
            print("roll no.", member_rol[0])
            def_mem = student.objects.get(reg_number=member_rol[0])
            if len(member_reg) == 1:
                prj = project(project_title=project_title, group_name=group_name, course_code=course_code,
                              session=session_val,
                              member1_reg=member_reg[0], member2_reg=def_mem, member3_reg=def_mem,
                              project_id=project_id)
                prj.save()
            elif len(member_reg) == 2:
                prj = project(project_title=project_title, group_name=group_name, course_code=course_code,
                              session=session_val,
                              member1_reg=member_reg[0], member2_reg=member_reg[1], member3_reg=def_mem,
                              project_id=project_id)
                prj.save()
            elif len(member_reg) == 3:
                prj = project(project_title=project_title, project_id=project_id, group_name=group_name,
                              course_code=course_code, session=session_val,
                              member1_reg=member_reg[0], member2_reg=member_reg[1], member3_reg=member_reg[2])
                prj.save()

        student_obj = student.objects.get(email=request.user)
        proj = []
        projects = project.objects.raw(
            "select * from student_project where member1_reg_id LIKE %s OR member2_reg_id LIKE %s OR member3_reg_id LIKE %s",
            [student_obj.reg_number, student_obj.reg_number, student_obj.reg_number])
        for x in projects:
            print(x)
        # print(projects
        type = "student"
        return render(request, 'student/student-home.html', {'projects': projects, 'type':type})

    elif request.user.is_authenticated and user_type.objects.get(user=request.user).is_teach:
        return redirect('thome')
    else:
        return redirect('home')


def load_sessions(request):
    if request.user.is_authenticated and user_type.objects.get(user=request.user).is_student:
        course_code = request.GET.get('course_code')
        sessions = session.objects.filter(course_code=course_code)
        type = "student"
        return render(request, 'student/session-dropdown-options.html', {'sessions': sessions, 'type':type})
    else:
        if request.user.is_authenticated and user_type.objects.get(user=request.user).is_teach:
            return redirect('thome')


def newproject(request):
    if request.user.is_authenticated and user_type.objects.get(user=request.user).is_student:
        course_ob = course.objects
        session_ob = session.objects
        student_ob = student.objects.exclude(reg_number='000')
        type = "student"
        return render(request, 'student/new-project.html',
                      {'course': course_ob, 'student': student_ob, 'sessions': session_ob, 'type':type})
    else:
        if request.user.is_authenticated and user_type.objects.get(user=request.user).is_teach:
            return redirect('thome')


       

def projectdetails(request, project_id):
    if request.user.is_authenticated:
        project_obj = get_object_or_404(project, pk=project_id)
        student_obj = student.objects.get(email=request.user)
        course_code = project_obj.course_code
        sessions = session.objects.get(course_code=course_code)
        if request.method == 'POST' :
                ok = False
                for uploaded_file in request.FILES.getlist('file'):
                    # uploaded_file = request.FILES['file']
                    # fs = FileSystemStorage()
                    # fs.save(uploaded_file.name, uploaded_file)
                    size = uploaded_file.size

                    ext = ""
                    if size < 512000:
                        size = size / 1024.0
                        ext = 'Kb'
                    elif size < 4194304000:
                        size = size / 1048576.0
                        ext = 'Mb'
                    else:
                        size = size / 1073741824.0
                        ext = 'Gb'
                    value = '%.2f' % size
                    value = value + ext
                    # print(value)
                    project_ob = project.objects.get(project_id=request.POST.get("project_id"))
                    file_obj = file(file_name=uploaded_file.name, project_id=project_ob, file_content=uploaded_file,
                                    file_size=value)
                    file_obj.save()
                    # subject = 'New file uploaded on App'
                    # message = f'{student_obj.name} ({student_obj.reg_number}) Uploaded a new file on IITJSHARE.' 
                    # from_email = 'jschouhan2325@gmail.com'
                    # recipient_list = ['singh.126@iitj.ac.in']
                    # send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    # sent = True
                    print("jeevan") 
                   
                    print(course_code)  
                    
                    
                    s1 = project_obj.member1_reg  
                    s2 = project_obj.member2_reg  
                    s3 = project_obj.member3_reg 
                    lst = [s1.email, s2.email, s3.email] 
                    tc = sessions.teacher_code.email
                    box = []
                    for mail in lst:
                        box.append(str(mail))
                    print("this")
                    print(tc.email)
                    email = EmailMessage(
                                    'New project file uploaded',
                                    f"{student_obj.name}({project_obj.group_name}) uploaded a new project file in {session.course_code} ",
                                    'jschouhan2325@gmail.com',
                                    to = [tc],
                                    bcc = lst,
                                    headers={'Cc': ', '.join(box)},
                                    )
                    #email.send()

        project_messages = project_obj.message_set.all().order_by('-created')
        Project = project.objects.get(pk=project_id)
        tc = sessions.teacher_code.email
        if request.method == 'POST' and request.POST.get('body') is not None:
            email = EmailMessage(
                'New message',
                f"{student_obj.name}({project_obj.group_name}) send you a message in {course_code} project section ",
                'jschouhan2325@gmail.com',
                to = [tc],)
            #email.send()
            print("jii", project_id)
            print("The name of the user is:", student_obj.name)
            student_obj = student.objects.get(email=request.user)
            message = Message.objects.create(
                user = request.user,
                project = project_obj,
                body = request.POST.get('body'),
                name = student_obj.name +'(' + student_obj.reg_number + ')'
            )
            return redirect('projectdetails', project_id)
        
        files = file.objects
        type = ""
        if user_type.objects.get(user=request.user).is_teach:
            type = "teach"
        else:
            type = "student"
        return render(request, 'upload.html', {'project_obj': project_obj, 'files': files, 'type':type, 'project_messages':project_messages})
    else:
        return redirect('home')


# def delete_file(self, *args, **kwargs):
#     print(self)
#     self.file_name.delete()
#     super.delete(*args, **kwargs)

def delete_file(request, pk):
    type = ""
    if user_type.objects.get(user=request.user).is_teach:
        type = "teach"
    else:
        type = "student"
    print("here--------------------------")
    if (request.method == "POST"):
        if request.POST.get('delete') is not None:
            project_id = request.POST.get('delete')
            file_obj = file.objects.get(pk=pk)
            file_obj.delete()
            #os.remove(os.path.join(settings.MEDIA_ROOT, request.POST.get('filename')))
            # print("vbvbvbvbv")
            project_ob = project.objects.get(project_id=project_id)
            project_messages = project_ob.message_set.all().order_by('-created')
            file_ob2 = file.objects
            course_code = project_ob.course_code
            sessions = session.objects.get(course_code=course_code)
            if type == "student" :
                next_url = request.POST.get('next', reverse('projectdetails',args=[project_ob.project_id]))
            else:
                next_url = request.POST.get('next', reverse('projectdetails',args=[sessions.session_id, project_ob.project_id,]))
            return redirect(next_url)     
    else:
        return redirect('upload.html')