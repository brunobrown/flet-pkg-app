"""Hooks that bridge presentation state with domain use cases."""

from src.domain.usecases.get_home_data import GetHomeDataUseCase
from src.domain.usecases.get_package_detail import GetPackageDetailUseCase
from src.domain.usecases.search_packages import SearchPackagesUseCase
from src.domain.usecases.star_package import StarPackageUseCase
from src.presentation.state_management.global_state import PackagesState, UserState
from src.services.api_service import ApiService


async def load_home_data(state: PackagesState, api: ApiService, pypi_only: bool = True) -> None:
    state.home_loading = True
    state.error = ""
    try:
        use_case = GetHomeDataUseCase(api.repository)
        state.home_data = await use_case.execute(pypi_only=pypi_only)
    except Exception as e:
        state.error = str(e)
    finally:
        state.home_loading = False


async def search_packages(
    state: PackagesState,
    api: ApiService,
    query: str = "",
    page_num: int = 1,
    pypi_only: bool = True,
) -> None:
    state.is_loading = True
    state.error = ""
    state.search_query = query
    state.page_number = page_num
    try:
        use_case = SearchPackagesUseCase(api.repository)
        packages, total = await use_case.execute(
            query=query,
            page=page_num,
            per_page=state.per_page,
            sort=state.sort_by,
            package_type=state.filter_type,
            official_only=state.filter_official,
            pypi_only=pypi_only,
        )
        state.packages = packages
        state.total_count = total
    except Exception as e:
        state.error = str(e)
        state.packages = []
        state.total_count = 0
    finally:
        state.is_loading = False


async def load_package_detail_by_name(
    state: PackagesState, api: ApiService, package_name: str
) -> None:
    state.detail_loading = True
    state.detail_package_name = package_name
    state.error = ""
    try:
        use_case = GetPackageDetailUseCase(api.repository)
        state.detail_package = await use_case.execute_by_name(package_name)
    except Exception as e:
        state.error = str(e)
        state.detail_package = None
    finally:
        state.detail_loading = False


async def toggle_star(
    state: PackagesState, user: UserState, api: ApiService, owner: str, repo: str
) -> bool:
    if not user.github_token:
        return False
    use_case = StarPackageUseCase(api.repository)
    is_starred = await use_case.is_starred(owner, repo, user.github_token)
    if is_starred:
        await use_case.unstar(owner, repo, user.github_token)
        return False
    else:
        await use_case.star(owner, repo, user.github_token)
        return True
