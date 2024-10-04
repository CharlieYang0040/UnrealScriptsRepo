# WBP_MakeLight

## 목차

1. 파일 구성 및 설치 방법
2. UI 및 기능 소개
3. 사용 예시
4. 버전 기록

## 1. 파일 구성 및 설치 방법

[**다운로드**](https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/WBP_MakeLight/WBP_MakeLight.uasset) https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/WBP_MakeLight/WBP_MakeLight.uasset


![image](https://github.com/user-attachments/assets/4cbf95e2-610e-46ee-aa15-5d95def5a2d2)

![image](https://github.com/user-attachments/assets/c7c7c6cc-63f9-4af1-bec7-75c05e1aea09)


- WBP_MakeLight.uasset를 프로젝트 폴더의 Content 폴더 하위의 원하는 위치에 넣는다.

![image (2)](https://github.com/user-attachments/assets/83346c82-c058-4d16-b81d-a5530b181120)



![image](https://github.com/user-attachments/assets/d80da976-9f4e-46ee-8cca-227783010b1f)



- MakeLight 폴더는 플러그인의 정보를 담는 .uplugin 파일과 코드들이 컴파일 되어있는 Binaries 폴더로 이루어져 있다.

## 2. UI 및 기능 소개

![image (5)](https://github.com/user-attachments/assets/66d1a93a-8dd9-4614-9f40-c734d2bbba32)


- 조명 종류 : 생성할 라이트의 종류를 선택한다. Spot, Rect, Point
- 조명 용도 : 생성할 라이트의 용도를 선택한다. 
Key, Fill, LeftRim, RightRim - 사전 설정된 위치로 생성된다.
ThreePoint - Key, Fill, LeftRim, RightRim을 모두 한번에 생성한다.
None - 원점에 생성한다.
- 부착할 본 : 어태치할 본을 선택한다.
Head, Spine - 각 Bip001-Head, Bip001-Spine2에 어태치한다.
None - 본이 아닌 액터에 어태치한다.
Custom - 우측의 “Custom 본 이름 입력” 창에 입력된 본의 이름으로 어태치한다.
- 조명 생성 및 부착 : 설정된 라이트를 생성하고 선택한 액터에 어태치한다.
- 기존 조명 부착 : 첫번째로 선택한 조명을 두번째로 선택한 액터에 부착한다.

## 3. 사용 예시

- 기본 라이팅 세팅하기
    
   ![기본라이팅세팅하기](https://github.com/user-attachments/assets/04196436-afba-4f0b-a5cb-09e2616e94d8)


- 머리에 림라이트 생성하기
    
   ![머리림라이트생성하기](https://github.com/user-attachments/assets/fa4a8587-4174-4fa0-a9a6-c7e4ffd3660e)
    

- 기존 조명을 어태치하기
    
   ![기존조명을어태치하기](https://github.com/user-attachments/assets/fd6aead0-6acd-470c-b4b3-05d75d312534)
    

- 원하는 본에 어태치하기
    
   ![원하는본에어태치하기](https://github.com/user-attachments/assets/4058dc40-2f87-48ea-ba1f-bb0af772ccbb)
    

## 4. 버전 기록

24.09.23 Alpha1 : https://github.com/CharlieYang0040/UnrealScriptsRepo/raw/refs/heads/main/MakeLight/MakeLight_Alpha1.zip
