import dateparser
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
import pkce

from fusionauth.fusionauth_client import FusionAuthClient


def get_or_create_user(user_id, request):
    user = User.objects.filter(username=user_id).first()
    if not user:
        user = User(username=user_id)
        user.save()
    return user


def get_login_url(request):
    if request.session.has_key('pkce_verifier') is False or request.session.has_key('code_challenge') is False:
        code_verifier = pkce.generate_code_verifier(length=128)
        code_challenge = pkce.get_code_challenge(code_verifier)
        request.session['pkce_verifier'] = code_verifier
        request.session['code_challenge'] = code_challenge
    redirect_url = request.build_absolute_uri(reverse("dashboard"))
    login_url = f"{settings.FUSION_AUTH_BASE_URL}/oauth2/authorize?client_id={settings.FUSION_AUTH_APP_ID}&redirect_uri={redirect_url}&response_type=code&code_challenge={request.session['code_challenge']}&code_challenge_method=S256"
    login_url = login_url.format(
        settings.FUSION_AUTH_BASE_URL, settings.FUSION_AUTH_APP_ID,
    )
    return login_url


def is_user_login_ok(request):
    print("starting login")
    client = FusionAuthClient(
        settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL
    )
    code = request.GET.get("code")
    if not code:
        print("no code")
        return False
    try:
        redirect_url = request.build_absolute_uri(reverse("dashboard"))
        r = client.exchange_o_auth_code_for_access_token_using_pkce(
            code,
            redirect_url,
            request.session['pkce_verifier'],
            settings.CLIENT_ID,
            settings.FUSION_AUTH_CLIENT_SECRET,
        )

        if r.was_successful():
            print("all good")
            access_token = r.success_response["access_token"]
            user_id = r.success_response["userId"]
            get_or_create_user(user_id, request)
            return user_id
        else:
            print("could not exchange code for token")
            print(r.error_response)
            return False
    except Exception as e:
        print("Something went wrong")
        print(e)

class HomeView(View):
    def get(self, request):
        num_users = User.objects.count()
        login_url = get_login_url(request)
        return render(
            request,
            "secretbirthdaysapp/home.html",
            {"login_url": login_url, "num_users": num_users},
        )

class DashboardView(View):
    def get(self, request):

        user_id = is_user_login_ok(request)
        if not user_id:
            login_url = get_login_url(request)
            return redirect(login_url)

        user = None
        birthday = None
        try:
            client = FusionAuthClient(
                settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL
            )
            print(user_id)
            r = client.retrieve_user(user_id)
            print(request.user.username)
            if r.was_successful():
                birthday = r.success_response["user"].get("birthDate", 'unknown')
                print(birthday)
            else:
                print("coudln't get user")
                print(r.error_response)
            print("render dashboard with ", user_id)
            return render(request, "secretbirthdaysapp/dashboard.html", {"birthday": birthday, "user_id": user_id})
        except Exception as e:
            print("couldn't get user")
            print(e)
            return redirect(login_url)

    def post(self, request):

        birthday = request.POST.get("birthday")
        user_id = request.POST.get("user_id")
        normalised_birthday = None
        print(birthday)
        print(user_id)

        try:
            dt = dateparser.parse(birthday)
            normalised_birthday = dt.strftime("%Y-%m-%d")
        except Exception as e:
            print(e)
            print("Couldn't parse birthday")

        if not normalised_birthday:
            return render(
                request,
                "secretbirthdaysapp/dashboard.html",
                {"message": "Couldn't parse birthday. Please use YYYY-MM-DD",
                    "user_id": user_id},
            )

        try:
            client = FusionAuthClient(
                settings.FUSION_AUTH_API_KEY, settings.FUSION_AUTH_BASE_URL
            )
            r = client.patch_user(
                user_id, {"user": {"birthDate": normalised_birthday}}
            )
            if r.was_successful():
                print(r.success_response)
                return render(
                    request,
                    "secretbirthdaysapp/dashboard.html",
                    {
                        "message": "Updated your birthday",
                        "birthday": normalised_birthday,
                        "user_id": user_id,
                    },
                )
            else:
                print(r.error_response)
                return render(
                    request,
                    "secretbirthdaysapp/dashboard.html",
                    {"message": "Something went wrong",
                        "user_id": user_id},
                )
        except Exception as e:
            print(e)
            return render(
                request,
                "secretbirthdaysapp/dashboard.html",
                {"message": "Something went wrong"},
            )





class LogoutView(View):
    def get(self, request, *args, **kwargs):
        request.session.clear()
        redirect_url = request.build_absolute_uri("home")
        url = f"{settings.FUSION_AUTH_BASE_URL}/oauth2/logout?client_id={settings.FUSION_AUTH_APP_ID}"
        return redirect(url)
